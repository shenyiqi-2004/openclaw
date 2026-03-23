import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("post-run memory hooks", () => {
  const queueExternalMemoryKernelRun = vi.fn();

  beforeEach(() => {
    vi.resetModules();
    queueExternalMemoryKernelRun.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("maps gateway chat outcomes into gateway-chat events", async () => {
    vi.doMock("./external-memory-kernel.js", () => ({
      queueExternalMemoryKernelRun,
    }));
    const hooks = await import("./post-run-memory.js");

    hooks.emitGatewayChatPostRunMemory({
      outcome: "success",
      sessionKey: "session-1",
      requestId: "run-1",
    });

    expect(queueExternalMemoryKernelRun).toHaveBeenCalledWith({
      source: "gateway-chat",
      status: "success",
      sessionKey: "session-1",
      requestId: "run-1",
    });
  });

  it("maps gateway agent outcomes into gateway-agent events", async () => {
    vi.doMock("./external-memory-kernel.js", () => ({
      queueExternalMemoryKernelRun,
    }));
    const hooks = await import("./post-run-memory.js");

    hooks.emitGatewayAgentPostRunMemory({
      outcome: "error",
      sessionKey: "session-2",
      requestId: "run-2",
    });

    expect(queueExternalMemoryKernelRun).toHaveBeenCalledWith({
      source: "gateway-agent",
      status: "error",
      sessionKey: "session-2",
      requestId: "run-2",
    });
  });

  it("maps reply-agent outcomes into reply-agent events", async () => {
    vi.doMock("./external-memory-kernel.js", () => ({
      queueExternalMemoryKernelRun,
    }));
    const hooks = await import("./post-run-memory.js");

    hooks.emitReplyAgentPostRunMemory({
      outcome: "final",
      sessionKey: "session-3",
      agentId: "agent-3",
      requestId: "message-3",
    });

    expect(queueExternalMemoryKernelRun).toHaveBeenCalledWith({
      source: "reply-agent",
      status: "final",
      sessionKey: "session-3",
      agentId: "agent-3",
      requestId: "message-3",
    });
  });
});
