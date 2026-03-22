import { EventEmitter } from "node:events";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("node:child_process", () => ({
  spawn: vi.fn(),
}));

type KernelModule = typeof import("./external-memory-kernel.js");

async function makeMemoryRoot(): Promise<string> {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "openclaw-memory-kernel-"));
  await fs.mkdir(path.join(root, "memory"), { recursive: true });
  await fs.writeFile(path.join(root, "main.py"), "print('ok')\n", "utf8");
  return root;
}

function makeChildProcessStub(): EventEmitter {
  return new EventEmitter();
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

async function appendAck(pathname: string, eventId: string): Promise<void> {
  await fs.appendFile(
    pathname,
    `${JSON.stringify({ event_id: eventId, ack: true, timestamp: "2026-03-20T00:00:00Z" })}\n`,
    "utf8",
  );
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

  it("persists skipped events and replays them before newer events", async () => {
    const { spawn } = await import("node:child_process");
    const spawnMock = vi.mocked(spawn);
    const firstChild = makeChildProcessStub();
    const replayChild = makeChildProcessStub();
    spawnMock.mockReturnValueOnce(firstChild as never).mockReturnValueOnce(replayChild as never);

    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-chat",
        status: "success",
        sessionKey: "session-1",
      }),
    ).toBe(true);

    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-agent",
        status: "success",
        sessionKey: "session-2",
      }),
    ).toBe(false);

    const journalPaths = kernel.getExternalMemoryJournalPathsForTest(root);
    const recoveryBefore = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<string, { processing_state: string; skip_reason?: string }>;
    };
    expect(recoveryBefore.order).toHaveLength(2);
    const secondEventId = recoveryBefore.order[1];
    expect(recoveryBefore.events[secondEventId]?.processing_state).toBe("skipped");
    expect(recoveryBefore.events[secondEventId]?.skip_reason).toBe("active-run");

    const firstEventId = recoveryBefore.order[0];
    await appendAck(journalPaths.acks, firstEventId);
    firstChild.emit("exit", 0);
    await kernel.waitForExternalMemoryKernelIdleForTest();

    vi.setSystemTime(new Date("2026-03-20T00:00:03Z"));
    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "reply-agent",
        status: "final",
        sessionKey: "session-3",
      }),
    ).toBe(true);

    const secondSpawnCall = spawnMock.mock.calls[1];
    expect(secondSpawnCall?.[2]?.env?.OPENCLAW_MEMORY_SESSION_KEY).toBe("session-2");
    expect(secondSpawnCall?.[2]?.env?.OPENCLAW_MEMORY_REPLAY).toBe("1");

    await appendAck(journalPaths.acks, secondEventId);
    replayChild.emit("exit", 0);
    await kernel.waitForExternalMemoryKernelIdleForTest();

    const recoveryAfter = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<string, { processing_state: string }>;
    };
    expect(recoveryAfter.events[secondEventId]?.processing_state).toBe("committed");
    const latestEventId = recoveryAfter.order[2];
    expect(recoveryAfter.events[latestEventId]?.processing_state).toBe("pending");

    const traces = (await readJsonl(journalPaths.traces)) as Array<{
      action?: string;
      reason?: string;
    }>;
    expect(
      traces.some((record) => record.action === "launch_skipped" && record.reason === "active-run"),
    ).toBe(true);
  });

  it("records failed exits for later replay", async () => {
    const { spawn } = await import("node:child_process");
    const spawnMock = vi.mocked(spawn);
    const child = makeChildProcessStub();
    spawnMock.mockReturnValueOnce(child as never);

    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-chat",
        status: "error",
        sessionKey: "session-fail",
      }),
    ).toBe(true);

    child.emit("exit", 2);
    await kernel.waitForExternalMemoryKernelIdleForTest();

    const journalPaths = kernel.getExternalMemoryJournalPathsForTest(root);
    const recovery = (await readJson(journalPaths.recovery)) as {
      order: string[];
      events: Record<
        string,
        { processing_state: string; failure_reason?: string; replayable?: boolean }
      >;
    };
    const failedEventId = recovery.order[0];
    expect(recovery.events[failedEventId]?.processing_state).toBe("failed");
    expect(recovery.events[failedEventId]?.failure_reason).toBe("exit:2");
    expect(recovery.events[failedEventId]?.replayable).toBe(true);

    const commits = (await readJsonl(journalPaths.commits)) as Array<{ outcome?: string }>;
    expect(commits.some((record) => record.outcome === "failed")).toBe(true);

    const traces = (await readJsonl(journalPaths.traces)) as Array<{
      action?: string;
      exit_code?: number;
    }>;
    expect(traces.some((record) => record.action === "launch_exit" && record.exit_code === 2)).toBe(
      true,
    );
  });

  it("treats zero-exit runs without ack as replayable failure", async () => {
    const { spawn } = await import("node:child_process");
    const spawnMock = vi.mocked(spawn);
    const child = makeChildProcessStub();
    spawnMock.mockReturnValueOnce(child as never);

    expect(
      kernel.queueExternalMemoryKernelRun({
        source: "gateway-chat",
        status: "success",
        sessionKey: "session-no-ack",
      }),
    ).toBe(true);

    child.emit("exit", 0);
    await kernel.waitForExternalMemoryKernelIdleForTest();

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
    expect(recovery.events[eventId]?.failure_reason).toBe("ack-missing");
    expect(recovery.events[eventId]?.replayable).toBe(true);
  });
});
