import { describe, expect, it } from "vitest";
import { describeOpenClawRuntimeArtifacts } from "./openclaw-runtime-artifacts.js";

describe("openclaw runtime artifacts", () => {
  it("summarizes build, runtime, and memory artifact paths", () => {
    const summary = describeOpenClawRuntimeArtifacts();

    expect(summary.entry.cli.endsWith("openclaw.mjs")).toBe(true);
    expect(
      summary.build.distDir.endsWith("/dist") || summary.build.distDir.endsWith("\\dist"),
    ).toBe(true);
    expect(summary.paths.externalMemoryTracePath.includes("traces.jsonl")).toBe(true);
    expect(summary.memory.fallbackBackend).toBe("json_snapshot");
  });
});
