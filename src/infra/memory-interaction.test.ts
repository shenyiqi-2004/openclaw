import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("memory interaction boundary", () => {
  let stateDir: string;

  beforeEach(async () => {
    vi.resetModules();
    stateDir = await fs.mkdtemp(path.join(os.tmpdir(), "openclaw-memory-interaction-"));
  });

  afterEach(async () => {
    delete process.env.OPENCLAW_STATE_DIR;
    delete process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;
    delete process.env.OPENCLAW_RUNTIME_ROOT;
    await fs.rm(stateDir, { recursive: true, force: true });
  });

  it("describes configured canonical and fallback memory boundaries", async () => {
    process.env.OPENCLAW_STATE_DIR = stateDir;
    process.env.OPENCLAW_RUNTIME_ROOT = "/runtime/openclaw";
    process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT = "/runtime/openclaw/memory-sidecar";
    await fs.writeFile(
      path.join(stateDir, "openclaw.json"),
      JSON.stringify({
        plugins: {
          slots: { memory: "memory-lancedb-pro" },
          entries: {
            "memory-lancedb-pro": { enabled: true, config: { dbPath: "/tmp/lancedb-pro" } },
          },
        },
      }),
      "utf8",
    );

    const mod = await import("./memory-interaction.js");
    const info = mod.describeMemoryInteractionBoundary(process.env);

    expect(info.requestBoundary).toBe("durable-event-emit");
    expect(info.backgroundBoundary).toBe("sidecar-worker");
    expect(info.canonicalBackend).toBe("memory-lancedb-pro");
    expect(info.fallbackBackend).toBe("json_snapshot");
    expect(info.runtimeRoot).toBe("/runtime/openclaw");
    expect(info.externalMemoryRoot).toBe("/runtime/openclaw/memory-sidecar");
  });

  it("emits durable external memory events through the shared boundary", async () => {
    const queueExternalMemoryKernelRun = vi.fn(() => true);
    vi.doMock("./external-memory-kernel.js", () => ({
      queueExternalMemoryKernelRun,
    }));
    const mod = await import("./memory-interaction.js");

    const ok = mod.emitExternalMemoryInteraction({
      source: "gateway-chat",
      status: "success",
      sessionKey: "session-1",
      requestId: "req-1",
    });

    expect(ok).toBe(true);
    expect(queueExternalMemoryKernelRun).toHaveBeenCalledWith({
      source: "gateway-chat",
      status: "success",
      sessionKey: "session-1",
      requestId: "req-1",
    });
  });
});
