import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { createSubsystemLogger } from "../logging/subsystem.js";

const memoryLog = createSubsystemLogger("memory");
const DEFAULT_MEMORY_ROOT = "/mnt/d/openclaw";
const DEFAULT_PYTHON = "python3";
const MIN_RUN_INTERVAL_MS = 2_000;

let activeRun: Promise<void> | null = null;
let lastAttemptAt = 0;

function resolveMemoryRoot(): string | null {
  const root = process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT?.trim() || DEFAULT_MEMORY_ROOT;
  const mainPath = path.join(root, "main.py");
  if (!fs.existsSync(mainPath)) {
    return null;
  }
  return root;
}

function buildMemoryEnv(params: {
  source?: string;
  status?: string;
  sessionKey?: string;
  agentId?: string;
}): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = { ...process.env };
  if (params.source) {
    env.OPENCLAW_MEMORY_SOURCE = params.source;
  }
  if (params.status) {
    env.OPENCLAW_MEMORY_STATUS = params.status;
  }
  if (params.sessionKey) {
    env.OPENCLAW_MEMORY_SESSION_KEY = params.sessionKey;
  }
  if (params.agentId) {
    env.OPENCLAW_MEMORY_AGENT_ID = params.agentId;
  }
  return env;
}

export function queueExternalMemoryKernelRun(params: {
  source: string;
  status: "success" | "final" | "error";
  sessionKey?: string;
  agentId?: string;
}): boolean {
  if (process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY === "1") {
    return false;
  }
  const root = resolveMemoryRoot();
  if (!root) {
    return false;
  }
  const now = Date.now();
  if (activeRun || now - lastAttemptAt < MIN_RUN_INTERVAL_MS) {
    return false;
  }
  lastAttemptAt = now;

  activeRun = new Promise<void>((resolve) => {
    const child = spawn(
      process.env.OPENCLAW_EXTERNAL_MEMORY_PYTHON?.trim() || DEFAULT_PYTHON,
      ["main.py"],
      {
        cwd: root,
        env: buildMemoryEnv(params),
        stdio: "ignore",
      },
    );

    child.once("error", (err) => {
      memoryLog.warn(`external memory kernel launch failed: ${String(err)}`);
      resolve();
    });

    child.once("exit", (code) => {
      if (code !== 0) {
        memoryLog.warn(`external memory kernel exited with code ${String(code)}`);
      }
      resolve();
    });
  }).finally(() => {
    activeRun = null;
  });

  return true;
}

export async function waitForExternalMemoryKernelIdleForTest(): Promise<void> {
  await activeRun;
}
