import { spawn } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createSubsystemLogger } from "../logging/subsystem.js";

const memoryLog = createSubsystemLogger("memory");
const DEFAULT_MEMORY_ROOT = "/home/park/openclaw/memory-sidecar";
const DEFAULT_PYTHON = "python3";
const MIN_RUN_INTERVAL_MS = 2_000;
const MEMORY_STATE_DIR = "memory";
const EVENTS_JOURNAL_FILE = "events.jsonl";
const COMMITS_JOURNAL_FILE = "commits.jsonl";
const TRACES_JOURNAL_FILE = "traces.jsonl";
const RECOVERY_FILE = "recovery.json";
const ACKS_JOURNAL_FILE = "acks.jsonl";

type QueueExternalMemoryKernelRunParams = {
  source: string;
  status: "success" | "final" | "error";
  sessionKey?: string;
  agentId?: string;
};

type ProcessingState = "pending" | "processing" | "committed" | "failed" | "skipped";

type ExternalMemoryEventRecord = {
  event_id: string;
  timestamp: string;
  source: string;
  session_key?: string;
  agent_id?: string;
  status: "success" | "final" | "error";
  payload_hash: string;
  attempt_count: number;
  processing_state: ProcessingState;
  skip_reason?: string;
  failure_reason?: string;
  replayable: boolean;
  updated_at: string;
};

type ExternalMemoryRecoveryState = {
  version: 1;
  order: string[];
  events: Record<string, ExternalMemoryEventRecord>;
};

type ExternalMemoryTraceRecord = {
  timestamp: string;
  level: "info" | "warn";
  action:
    | "event_persisted"
    | "launch_skipped"
    | "launch_started"
    | "launch_error"
    | "launch_exit"
    | "commit_written"
    | "root_resolution_failed";
  event_id?: string;
  replayed?: boolean;
  reason?: string;
  source?: string;
  session_key?: string;
  agent_id?: string;
  status?: "success" | "final" | "error";
  exit_code?: number | null;
  memory_root?: string;
  attempt_count?: number;
  stdout_excerpt?: string;
  stderr_excerpt?: string;
};

const EMPTY_RECOVERY_STATE: ExternalMemoryRecoveryState = {
  version: 1,
  order: [],
  events: {},
};

let activeRun: Promise<void> | null = null;
let lastAttemptAt = 0;

function nowIso(): string {
  return new Date().toISOString();
}

function getConfiguredMemoryRoot(): string {
  return process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT?.trim() || DEFAULT_MEMORY_ROOT;
}

function getJournalPaths(root: string) {
  const memoryDir = path.join(root, MEMORY_STATE_DIR);
  return {
    memoryDir,
    events: path.join(memoryDir, EVENTS_JOURNAL_FILE),
    commits: path.join(memoryDir, COMMITS_JOURNAL_FILE),
    traces: path.join(memoryDir, TRACES_JOURNAL_FILE),
    recovery: path.join(memoryDir, RECOVERY_FILE),
    acks: path.join(memoryDir, ACKS_JOURNAL_FILE),
  };
}

function isDirectory(pathname: string): boolean {
  try {
    return fs.statSync(pathname).isDirectory();
  } catch {
    return false;
  }
}

function resolveRunnableMemoryRoot(root: string): boolean {
  return fs.existsSync(path.join(root, "main.py"));
}

function ensureJournalDir(root: string): boolean {
  if (!isDirectory(root)) {
    return false;
  }
  fs.mkdirSync(getJournalPaths(root).memoryDir, { recursive: true, mode: 0o700 });
  return true;
}

function appendJsonl(pathname: string, record: unknown): void {
  fs.appendFileSync(pathname, `${JSON.stringify(record)}\n`, "utf8");
}

function loadRecoveryState(root: string): ExternalMemoryRecoveryState {
  const { recovery } = getJournalPaths(root);
  try {
    if (!fs.existsSync(recovery)) {
      return { ...EMPTY_RECOVERY_STATE };
    }
    const raw = fs.readFileSync(recovery, "utf8");
    const parsed = JSON.parse(raw) as Partial<ExternalMemoryRecoveryState>;
    return {
      version: 1,
      order: Array.isArray(parsed.order)
        ? parsed.order.filter((value): value is string => typeof value === "string")
        : [],
      events: parsed.events && typeof parsed.events === "object" ? parsed.events : {},
    };
  } catch {
    return { ...EMPTY_RECOVERY_STATE };
  }
}

function saveRecoveryState(root: string, data: ExternalMemoryRecoveryState): void {
  const { recovery } = getJournalPaths(root);
  fs.writeFileSync(recovery, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function writeTrace(root: string, record: ExternalMemoryTraceRecord): void {
  appendJsonl(getJournalPaths(root).traces, record);
}

function updateRecoveryEvent(
  root: string,
  eventId: string,
  update: Partial<ExternalMemoryEventRecord>,
): ExternalMemoryEventRecord | null {
  const state = loadRecoveryState(root);
  const current = state.events[eventId];
  if (!current) {
    return null;
  }
  const next: ExternalMemoryEventRecord = {
    ...current,
    ...update,
    updated_at: nowIso(),
  };
  state.events[eventId] = next;
  saveRecoveryState(root, state);
  return next;
}

function buildPayloadHash(params: QueueExternalMemoryKernelRunParams): string {
  return createHash("sha256")
    .update(
      JSON.stringify({
        source: params.source,
        status: params.status,
        sessionKey: params.sessionKey ?? "",
        agentId: params.agentId ?? "",
      }),
    )
    .digest("hex");
}

function persistEvent(
  root: string,
  params: QueueExternalMemoryKernelRunParams,
): ExternalMemoryEventRecord {
  const timestamp = nowIso();
  const record: ExternalMemoryEventRecord = {
    event_id: randomUUID(),
    timestamp,
    source: params.source,
    session_key: params.sessionKey,
    agent_id: params.agentId,
    status: params.status,
    payload_hash: buildPayloadHash(params),
    attempt_count: 0,
    processing_state: "pending",
    replayable: true,
    updated_at: timestamp,
  };
  appendJsonl(getJournalPaths(root).events, record);
  const state = loadRecoveryState(root);
  state.order.push(record.event_id);
  state.events[record.event_id] = record;
  saveRecoveryState(root, state);
  writeTrace(root, {
    timestamp,
    level: "info",
    action: "event_persisted",
    event_id: record.event_id,
    source: record.source,
    session_key: record.session_key,
    agent_id: record.agent_id,
    status: record.status,
    memory_root: root,
  });
  return record;
}

function findReplayableEvent(root: string): ExternalMemoryEventRecord | null {
  const state = loadRecoveryState(root);
  for (const eventId of state.order) {
    const event = state.events[eventId];
    if (!event) {
      continue;
    }
    if (!event.replayable) {
      continue;
    }
    if (
      event.processing_state === "pending" ||
      event.processing_state === "skipped" ||
      event.processing_state === "failed"
    ) {
      return event;
    }
  }
  return null;
}

function appendCommitRecord(
  root: string,
  event: ExternalMemoryEventRecord,
  outcome: "committed" | "failed",
): void {
  appendJsonl(getJournalPaths(root).commits, {
    timestamp: nowIso(),
    event_id: event.event_id,
    source: event.source,
    session_key: event.session_key,
    agent_id: event.agent_id,
    status: event.status,
    outcome,
    attempt_count: event.attempt_count,
  });
}

function hasAckRecord(root: string, eventId: string): boolean {
  const { acks } = getJournalPaths(root);
  if (!fs.existsSync(acks)) {
    return false;
  }
  try {
    const raw = fs.readFileSync(acks, "utf8");
    const lines = raw.split("\n");
    for (let index = lines.length - 1; index >= 0; index -= 1) {
      const line = lines[index]?.trim();
      if (!line) {
        continue;
      }
      const parsed = JSON.parse(line) as Record<string, unknown>;
      if (parsed.event_id === eventId && parsed.ack === true) {
        return true;
      }
    }
  } catch {
    return false;
  }
  return false;
}

function buildMemoryEnv(event: ExternalMemoryEventRecord, replayed: boolean): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = { ...process.env };
  env.OPENCLAW_MEMORY_SOURCE = event.source;
  env.OPENCLAW_MEMORY_STATUS = event.status;
  env.OPENCLAW_MEMORY_EVENT_ID = event.event_id;
  env.OPENCLAW_MEMORY_REPLAY = replayed ? "1" : "0";
  if (event.session_key) {
    env.OPENCLAW_MEMORY_SESSION_KEY = event.session_key;
  }
  if (event.agent_id) {
    env.OPENCLAW_MEMORY_AGENT_ID = event.agent_id;
  }
  return env;
}

export function getExternalMemoryJournalPathsForTest(root: string) {
  return getJournalPaths(root);
}

export function resetExternalMemoryKernelForTest(): void {
  activeRun = null;
  lastAttemptAt = 0;
}

export function queueExternalMemoryKernelRun(params: QueueExternalMemoryKernelRunParams): boolean {
  const configuredRoot = getConfiguredMemoryRoot();
  const journalAvailable = ensureJournalDir(configuredRoot);
  const persistedEvent = journalAvailable ? persistEvent(configuredRoot, params) : null;

  if (process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY === "1") {
    if (journalAvailable && persistedEvent) {
      updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
        processing_state: "skipped",
        skip_reason: "disabled",
        replayable: false,
      });
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: "info",
        action: "launch_skipped",
        event_id: persistedEvent.event_id,
        source: persistedEvent.source,
        status: persistedEvent.status,
        reason: "disabled",
        memory_root: configuredRoot,
      });
    }
    return false;
  }

  if (!resolveRunnableMemoryRoot(configuredRoot)) {
    if (journalAvailable && persistedEvent) {
      updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
        processing_state: "skipped",
        skip_reason: "memory-root-missing",
        replayable: false,
      });
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: "warn",
        action: "root_resolution_failed",
        event_id: persistedEvent.event_id,
        source: persistedEvent.source,
        status: persistedEvent.status,
        reason: "memory-root-missing",
        memory_root: configuredRoot,
      });
    }
    return false;
  }

  const now = Date.now();
  if (activeRun) {
    if (journalAvailable && persistedEvent) {
      updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
        processing_state: "skipped",
        skip_reason: "active-run",
        replayable: true,
      });
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: "info",
        action: "launch_skipped",
        event_id: persistedEvent.event_id,
        source: persistedEvent.source,
        status: persistedEvent.status,
        reason: "active-run",
        memory_root: configuredRoot,
      });
    }
    return false;
  }

  if (now - lastAttemptAt < MIN_RUN_INTERVAL_MS) {
    if (journalAvailable && persistedEvent) {
      updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
        processing_state: "skipped",
        skip_reason: "throttled",
        replayable: true,
      });
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: "info",
        action: "launch_skipped",
        event_id: persistedEvent.event_id,
        source: persistedEvent.source,
        status: persistedEvent.status,
        reason: "throttled",
        memory_root: configuredRoot,
      });
    }
    return false;
  }

  const selected = findReplayableEvent(configuredRoot);
  if (!selected) {
    return false;
  }
  const replayed = persistedEvent ? selected.event_id !== persistedEvent.event_id : true;
  const processingEvent = updateRecoveryEvent(configuredRoot, selected.event_id, {
    processing_state: "processing",
    skip_reason: undefined,
    failure_reason: undefined,
    attempt_count: selected.attempt_count + 1,
  });
  if (!processingEvent) {
    return false;
  }

  lastAttemptAt = now;
  writeTrace(configuredRoot, {
    timestamp: nowIso(),
    level: "info",
    action: "launch_started",
    event_id: processingEvent.event_id,
    replayed,
    source: processingEvent.source,
    session_key: processingEvent.session_key,
    agent_id: processingEvent.agent_id,
    status: processingEvent.status,
    memory_root: configuredRoot,
    attempt_count: processingEvent.attempt_count,
  });

  activeRun = new Promise<void>((resolve) => {
    let stdoutBuffer = "";
    let stderrBuffer = "";
    const child = spawn(
      process.env.OPENCLAW_EXTERNAL_MEMORY_PYTHON?.trim() || DEFAULT_PYTHON,
      ["main.py"],
      {
        cwd: configuredRoot,
        env: buildMemoryEnv(processingEvent, replayed),
        stdio: ["ignore", "pipe", "pipe"],
      },
    );
    child.stdout?.on("data", (chunk) => {
      stdoutBuffer = `${stdoutBuffer}${String(chunk)}`.slice(-4000);
    });
    child.stderr?.on("data", (chunk) => {
      stderrBuffer = `${stderrBuffer}${String(chunk)}`.slice(-4000);
    });

    child.once("error", (err) => {
      const next = updateRecoveryEvent(configuredRoot, processingEvent.event_id, {
        processing_state: "failed",
        failure_reason: String(err),
        replayable: true,
      });
      if (next) {
        appendCommitRecord(configuredRoot, next, "failed");
      }
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: "warn",
        action: "launch_error",
        event_id: processingEvent.event_id,
        replayed,
        source: processingEvent.source,
        session_key: processingEvent.session_key,
        agent_id: processingEvent.agent_id,
        status: processingEvent.status,
        reason: String(err),
        memory_root: configuredRoot,
        attempt_count: processingEvent.attempt_count,
        stdout_excerpt: stdoutBuffer || undefined,
        stderr_excerpt: stderrBuffer || undefined,
      });
      memoryLog.warn(`external memory kernel launch failed: ${String(err)}`);
      resolve();
    });

    child.once("exit", (code) => {
      const acked = code === 0 && hasAckRecord(configuredRoot, processingEvent.event_id);
      if (acked) {
        const next = updateRecoveryEvent(configuredRoot, processingEvent.event_id, {
          processing_state: "committed",
          replayable: false,
          failure_reason: undefined,
        });
        if (next) {
          appendCommitRecord(configuredRoot, next, "committed");
          writeTrace(configuredRoot, {
            timestamp: nowIso(),
            level: "info",
            action: "commit_written",
            event_id: next.event_id,
            replayed,
            source: next.source,
            session_key: next.session_key,
            agent_id: next.agent_id,
            status: next.status,
            memory_root: configuredRoot,
            attempt_count: next.attempt_count,
          });
        }
      } else {
        const reason = code === 0 ? "ack-missing" : `exit:${String(code)}`;
        const next = updateRecoveryEvent(configuredRoot, processingEvent.event_id, {
          processing_state: "failed",
          failure_reason: reason,
          replayable: true,
        });
        if (next) {
          appendCommitRecord(configuredRoot, next, "failed");
        }
      }
      writeTrace(configuredRoot, {
        timestamp: nowIso(),
        level: code === 0 ? "info" : "warn",
        action: "launch_exit",
        event_id: processingEvent.event_id,
        replayed,
        source: processingEvent.source,
        session_key: processingEvent.session_key,
        agent_id: processingEvent.agent_id,
        status: processingEvent.status,
        exit_code: code,
        reason: acked ? undefined : code === 0 ? "ack-missing" : `exit:${String(code)}`,
        memory_root: configuredRoot,
        attempt_count: processingEvent.attempt_count,
        stdout_excerpt: stdoutBuffer || undefined,
        stderr_excerpt: stderrBuffer || undefined,
      });
      if (!acked) {
        memoryLog.warn(
          code === 0
            ? `external memory kernel exited without ack for event ${processingEvent.event_id}`
            : `external memory kernel exited with code ${String(code)}`,
        );
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
