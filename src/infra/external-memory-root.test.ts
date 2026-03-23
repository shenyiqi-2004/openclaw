import { afterEach, describe, expect, it } from "vitest";
import {
  describeExternalMemoryRoot,
  resolveConfiguredExternalMemoryRoot,
} from "./external-memory-root.js";

describe("external-memory-root", () => {
  afterEach(() => {
    delete process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;
    delete process.env.OPENCLAW_RUNTIME_ROOT;
  });

  it("uses canonical defaults when no env is set", () => {
    const resolved = resolveConfiguredExternalMemoryRoot();
    expect(resolved.runtimeRoot).toBe("/home/park/openclaw");
    expect(resolved.memoryRoot).toBe("/home/park/openclaw/memory-sidecar");
    expect(resolved.source).toBe("default");
  });

  it("derives the memory root from OPENCLAW_RUNTIME_ROOT", () => {
    process.env.OPENCLAW_RUNTIME_ROOT = "/tmp/openclaw";
    const resolved = describeExternalMemoryRoot();
    expect(resolved.memoryRoot).toBe("/tmp/openclaw/memory-sidecar");
    expect(resolved.source).toBe("env:OPENCLAW_RUNTIME_ROOT");
  });

  it("marks deprecated roots when OPENCLAW_EXTERNAL_MEMORY_ROOT is old", () => {
    process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT = "/mnt/d/openclaw";
    const resolved = describeExternalMemoryRoot();
    expect(resolved.deprecated).toBe(true);
    expect(resolved.source).toBe("env:OPENCLAW_EXTERNAL_MEMORY_ROOT");
  });
});
