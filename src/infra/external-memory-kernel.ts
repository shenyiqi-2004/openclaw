import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createSubsystemLogger } from "../logging/subsystem.js";
import type {
  ExternalMemoryCorrelationRecord,
  ExternalMemoryEventRecord,
  ExternalMemoryRecoveryState,
  ExternalMemoryTraceRecord,
  ExternalMemoryTriggerStatus,
} from "./external-memory-records.js";
import { describeExternalMemoryRoot } from "./external-memory-root.js";
import { classifyExternalMemoryEmitWork } from "./runtime-work-model.js";

const memoryLog = createSubsystemLogger("memory");
const MEMORY_STATE_DIR = "memory";
const EVENTS_JOURNAL_FILE = "events.jsonl";
const COMMITS_JOURNAL_FILE = "commits.jsonl";
const TRACES_JOURNAL_FILE = "traces.jsonl";
const RECOVERY_FILE = "recovery.json";
const ACKS_JOURNAL_FILE = "acks.jsonl";

type QueueExternalMemoryKernelRunParams = {
  source: string;
  status: ExternalMemoryTriggerStatus;
  sessionKey?: string;
  agentId?: string;
  requestId?: string;
};

const EMPTY_RECOVERY_STATE: ExternalMemoryRecoveryState = {
  version: 1,
  order: [],
  events: {},
};

function nowIso(): string {
  return new Date().toISOString();
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

function buildTraceCorrelation(record: {
  event_id?: string;
  request_id?: string;
  attempt_count?: number;
  work_class?: string;
}): ExternalMemoryCorrelationRecord | undefined {
  if (!record.event_id || !record.request_id) {
    return undefined;
  }
  return {
    event_id: record.event_id,
    request_id: record.request_id,
    worker_task_id:
      typeof record.attempt_count === "number" && record.attempt_count > 0
        ? `${record.event_id}:${record.attempt_count}`
        : undefined,
    replay_attempt: record.attempt_count,
    work_class: record.work_class,
  };
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

function buildPayloadSummary(params: QueueExternalMemoryKernelRunParams): string {
  return [params.source, params.status, params.sessionKey ?? "", params.agentId ?? ""]
    .filter((value) => value.length > 0)
    .join(" | ");
}

function persistEvent(
  root: string,
  params: QueueExternalMemoryKernelRunParams,
): ExternalMemoryEventRecord {
  const timestamp = nowIso();
  const record: ExternalMemoryEventRecord = {
    event_id: randomUUID(),
    request_id: params.requestId?.trim() || randomUUID(),
    timestamp,
    source: params.source,
    session_key: params.sessionKey,
    agent_id: params.agentId,
    status: params.status,
    payload_hash: buildPayloadHash(params),
    payload_summary: buildPayloadSummary(params),
    attempt_count: 0,
    processing_state: "queued",
    replayable: true,
    updated_at: timestamp,
  };
  appendJsonl(getJournalPaths(root).events, record);
  const state = loadRecoveryState(root);
  state.order.push(record.event_id);
  state.events[record.event_id] = record;
  saveRecoveryState(root, state);
  return record;
}

export function getExternalMemoryJournalPathsForTest(root: string) {
  return getJournalPaths(root);
}

export function resetExternalMemoryKernelForTest(): void {
  return;
}

export type { QueueExternalMemoryKernelRunParams };

export function queueExternalMemoryKernelRun(params: QueueExternalMemoryKernelRunParams): boolean {
  const resolution = describeExternalMemoryRoot();
  const configuredRoot = resolution.memoryRoot;
  const journalAvailable = ensureJournalDir(configuredRoot);

  if (!journalAvailable) {
    memoryLog.warn(`external memory journal unavailable at ${configuredRoot}`);
    return false;
  }

  const persistedEvent = persistEvent(configuredRoot, params);
  writeTrace(configuredRoot, {
    timestamp: nowIso(),
    level: "info",
    action: "event_persisted",
    work_class: classifyExternalMemoryEmitWork(),
    event_id: persistedEvent.event_id,
    request_id: persistedEvent.request_id,
    source: persistedEvent.source,
    session_key: persistedEvent.session_key,
    agent_id: persistedEvent.agent_id,
    status: persistedEvent.status,
    memory_root: configuredRoot,
    runtime_root: resolution.runtimeRoot,
    root_source: resolution.source,
    deprecated_root: resolution.deprecated,
    correlation: buildTraceCorrelation({
      event_id: persistedEvent.event_id,
      request_id: persistedEvent.request_id,
      attempt_count: persistedEvent.attempt_count,
      work_class: classifyExternalMemoryEmitWork(),
    }),
  });

  if (process.env.OPENCLAW_DISABLE_EXTERNAL_MEMORY === "1") {
    updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
      processing_state: "failed",
      skip_reason: "disabled",
      replayable: false,
    });
    return false;
  }

  if (!resolveRunnableMemoryRoot(configuredRoot)) {
    updateRecoveryEvent(configuredRoot, persistedEvent.event_id, {
      processing_state: "failed",
      skip_reason: "memory-root-missing",
      failure_reason: "memory-root-missing",
      replayable: true,
    });
    writeTrace(configuredRoot, {
      timestamp: nowIso(),
      level: "warn",
      action: "root_resolution_failed",
      work_class: classifyExternalMemoryEmitWork(),
      event_id: persistedEvent.event_id,
      request_id: persistedEvent.request_id,
      source: persistedEvent.source,
      status: persistedEvent.status,
      reason: "memory-root-missing",
      memory_root: configuredRoot,
      runtime_root: resolution.runtimeRoot,
      root_source: resolution.source,
      deprecated_root: resolution.deprecated,
      correlation: buildTraceCorrelation({
        event_id: persistedEvent.event_id,
        request_id: persistedEvent.request_id,
        attempt_count: persistedEvent.attempt_count,
        work_class: classifyExternalMemoryEmitWork(),
      }),
    });
    return true;
  }

  writeTrace(configuredRoot, {
    timestamp: nowIso(),
    level: "info",
    action: "event_queued",
    work_class: classifyExternalMemoryEmitWork(),
    event_id: persistedEvent.event_id,
    request_id: persistedEvent.request_id,
    source: persistedEvent.source,
    session_key: persistedEvent.session_key,
    agent_id: persistedEvent.agent_id,
    status: persistedEvent.status,
    memory_root: configuredRoot,
    runtime_root: resolution.runtimeRoot,
    root_source: resolution.source,
    deprecated_root: resolution.deprecated,
    correlation: buildTraceCorrelation({
      event_id: persistedEvent.event_id,
      request_id: persistedEvent.request_id,
      attempt_count: persistedEvent.attempt_count,
      work_class: classifyExternalMemoryEmitWork(),
    }),
  });
  return true;
}

export async function waitForExternalMemoryKernelIdleForTest(): Promise<void> {
  return;
}
