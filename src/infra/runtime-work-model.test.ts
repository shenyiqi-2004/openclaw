import { describe, expect, it } from "vitest";
import { classifyExternalMemoryEmitWork, describeRuntimeWorkModel } from "./runtime-work-model.js";

describe("runtime work model", () => {
  it("describes the expected work buckets", () => {
    const model = describeRuntimeWorkModel();
    expect(model.requestTime.length).toBeGreaterThan(0);
    expect(model.postRequest).toContain("external memory durable emit");
    expect(model.background).toContain("sidecar worker loop");
    expect(model.recovery).toContain("event replay");
    expect(model.maintenance).toContain("health refresh");
  });

  it("classifies external memory emit as post-request work", () => {
    expect(classifyExternalMemoryEmitWork()).toBe("post-request");
  });
});
