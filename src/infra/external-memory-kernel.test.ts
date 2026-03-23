import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

type KernelModule = typeof import("./external-memory-kernel.js");

async function makeMemoryRoot(): Promise<string> {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "openclaw-memory-kernel-"));
  await fs.mkdir(path.join(root, "memory"), { recursive: true });
  await fs.writeFile(path.join(root, "main.py"), "print('ok')\n", "utf8");
  return root;
}

async function readJson(pathname: string): Promise<unknown> {
  return JSON.parse(await fs.readFile(pathname, "utf8"));
}

async function readJsonl(pathname: string): Promise<unknown[]> {
  const raw = await fs.readFile(pathname, "utf8");
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line) as unknown);
}

describe("external memory kernel", () => {
  let root: string;
  let kernel: KernelModule;

  beforeEach(async () => {
    vi.resetModules();
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-20T00:00:00Z"));
    root = await makeMemoryRoot();
    process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT = root;
    delete process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY;
    kernel = await import("./external-memory-kernel.js");
    kernel.resetExternalMemoryKernelForTest();
  });

  afterEach(async () => {
    kernel.resetExternalMemoryKernelForTest();
    vi.useRealTimers();
    delete process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;
    delete process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY;
    await fs.rm(root, { recursive: true, force: true });
  });

  it("persists a queued event without spawning the sidecar", async () => {
    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-chat",
        status: "success",
        sessionKey: "session-1",
      }),
    ).toBe(true);

    const journalPaths = kernel.getExternalMemoryJournalPathsForTest(root);
    const recovery = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<string, { processing_state: string; request_id?: string }>;
    };
    expect(recovery.order).toHaveLength(1);
    const eventId = recovery.order[0];
    expect(recovery.events[eventId]?.processing_state).toBe("queued");
    expect(typeof recovery.events[eventId]?.request_id).toBe("string");

    const traces = (await readJsonl(journalPaths.traces)) as Array<{
      action?: string;
      event_id?: string;
      request_id?: string;
      correlation?: { event_id?: string; request_id?: string };
    }>;
    const queuedTrace = traces.find((record) => record.action === "event_queued");
    expect(queuedTrace).toBeTruthy();
    expect(queuedTrace?.correlation?.event_id).toBe(queuedTrace?.event_id);
    expect(queuedTrace?.correlation?.request_id).toBe(queuedTrace?.request_id);
  });

  it("keeps a root-missing event replayable for later worker recovery", async () => {
    await fs.rm(path.join(root, "main.py"), { force: true });

    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-agent",
        status: "error",
        sessionKey: "session-2",
      }),
    ).toBe(true);

    const journalPaths = kernel.getExternalMemoryJournalPathsForTest(root);
    const recovery = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<
        string,
        { processing_state: string; failure_reason?: string; replayable?: boolean }
      >;
    };
    const eventId = recovery.order[0];
    expect(recovery.events[eventId]?.processing_state).toBe("failed");
    expect(recovery.events[eventId]?.failure_reason).toBe("memory-root-missing");
    expect(recovery.events[eventId]?.replayable).toBe(true);
    const traces = (await readJsonl(journalPaths.traces)) as Array<{
      action?: string;
      correlation?: { event_id?: string; request_id?: string };
    }>;
    const failedTrace = traces.find((record) => record.action === "root_resolution_failed");
    expect(failedTrace?.correlation?.event_id).toBe(eventId);
  });

  it("does not enqueue replayable work when external memory is disabled", async () => {
    process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY = "1";
    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "reply-agent",
        status: "final",
        sessionKey: "session-3",
      }),
    ).toBe(false);

    const journalPaths = kernel.getExternalMemoryJournalPathsForTest(root);
    const recovery = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<
        string,
        { processing_state: string; replayable?: boolean; skip_reason?: string }
      >;
    };
    const eventId = recovery.order[0];
    expect(recovery.events[eventId]?.processing_state).toBe("failed");
    expect(recovery.events[eventId]?.replayable).toBe(false);
    expect(recovery.events[eventId]?.skip_reason).toBe("disabled");
  });
});
