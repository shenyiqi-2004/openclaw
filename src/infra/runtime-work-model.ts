export type RuntimeWorkClass =
  | "request-time"
  | "post-request"
  | "background"
  | "recovery"
  | "maintenance";

export type RuntimeWorkModel = {
  requestTime: readonly string[];
  postRequest: readonly string[];
  background: readonly string[];
  recovery: readonly string[];
  maintenance: readonly string[];
};

const DEFAULT_RUNTIME_WORK_MODEL: RuntimeWorkModel = {
  requestTime: ["gateway chat", "gateway agent rpc", "auto-reply dispatch"],
  postRequest: ["external memory durable emit", "post-run completion hooks"],
  background: ["heartbeat runner", "gateway timers", "sidecar worker loop"],
  recovery: ["event replay", "restart sentinel wake", "stale lock cleanup"],
  maintenance: ["health refresh", "dedupe cleanup", "media cleanup"],
};

export function describeRuntimeWorkModel(): RuntimeWorkModel {
  return DEFAULT_RUNTIME_WORK_MODEL;
}

export function classifyExternalMemoryEmitWork(): RuntimeWorkClass {
  return "post-request";
}
