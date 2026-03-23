import { describe, expect, it, vi } from "vitest";

describe("runtimeLayoutStatusCommand", () => {
  it("prints JSON summary when requested", async () => {
    const log = vi.fn();
    const runtime = { log } as unknown as import("../runtime.js").RuntimeEnv;
    const mod = await import("./runtime-layout-status.js");

    await mod.runtimeLayoutStatusCommand({ json: true }, runtime);

    expect(log).toHaveBeenCalledTimes(1);
    const payload = JSON.parse(String(log.mock.calls[0]?.[0] ?? "{}")) as {
      paths?: { stateDir?: string };
      memory?: { canonicalBackend?: string };
    };
    expect(typeof payload.paths?.stateDir).toBe("string");
    expect(typeof payload.memory?.canonicalBackend).toBe("string");
  });
});
