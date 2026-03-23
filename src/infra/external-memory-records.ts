export type ExternalMemoryTriggerStatus = "success" | "final" | "error";

export type ExternalMemoryProcessingState = "queued" | "processing" | "acked" | "failed";

export type ExternalMemoryEventRecord = {
  event_id: string;
  request_id: string;
  timestamp: string;
  source: string;
  session_key?: string;
  agent_id?: string;
  status: ExternalMemoryTriggerStatus;
  payload_hash: string;
  payload_summary: string;
  attempt_count: number;
  processing_state: ExternalMemoryProcessingState;
  skip_reason?: string;
  failure_reason?: string;
  replayable: boolean;
  updated_at: string;
};

export type ExternalMemoryRecoveryState = {
  version: 1;
  order: string[];
  events: Record<string, ExternalMemoryEventRecord>;
};

export type ExternalMemoryCorrelationRecord = {
  request_id: string;
  event_id: string;
  worker_task_id?: string;
  runtime_step?: number;
  ack_id?: string;
  replay_attempt?: number;
  work_class?: string;
};

export type ExternalMemoryAckRecord = {
  timestamp: string;
  ack_id: string;
  event_id: string;
  request_id: string;
  source: string;
  status: ExternalMemoryTriggerStatus;
  session_key?: string;
  agent_id?: string;
  replayed: boolean;
  replay_attempt: number;
  ack: true;
  outcome: string;
  details: Record<string, unknown>;
  correlation?: ExternalMemoryCorrelationRecord;
};

export type ExternalMemoryCommitRecord = {
  timestamp: string;
  commit_id: string;
  event_id: string;
  request_id: string;
  source: string;
  status: ExternalMemoryTriggerStatus;
  session_key?: string;
  agent_id?: string;
  replayed: boolean;
  replay_attempt: number;
  outcome: string;
  ack_id?: string;
  runtime_step?: number;
  failure_reason?: string;
  correlation?: ExternalMemoryCorrelationRecord;
};

export type ExternalMemoryTraceRecord = {
  timestamp: string;
  level: "info" | "warn";
  action: "event_persisted" | "event_queued" | "root_resolution_failed";
  work_class?: string;
  event_id?: string;
  request_id?: string;
  reason?: string;
  source?: string;
  session_key?: string;
  agent_id?: string;
  status?: ExternalMemoryTriggerStatus;
  memory_root?: string;
  runtime_root?: string;
  root_source?: string;
  deprecated_root?: boolean;
  attempt_count?: number;
  correlation?: ExternalMemoryCorrelationRecord;
};
