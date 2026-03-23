import type { QueueExternalMemoryKernelRunParams } from "./external-memory-kernel.js";
import { emitExternalMemoryInteraction } from "./memory-interaction.js";

export type GatewayPostRunOutcome = "success" | "error";
export type ReplyAgentPostRunOutcome = "success" | "final";

function emitPostRunMemoryEvent(params: QueueExternalMemoryKernelRunParams): boolean {
  return emitExternalMemoryInteraction(params);
}

export function emitGatewayChatPostRunMemory(params: {
  outcome: GatewayPostRunOutcome;
  sessionKey?: string;
  requestId?: string;
}): boolean {
  return emitPostRunMemoryEvent({
    source: "gateway-chat",
    status: params.outcome,
    sessionKey: params.sessionKey,
    requestId: params.requestId,
  });
}

export function emitGatewayAgentPostRunMemory(params: {
  outcome: GatewayPostRunOutcome;
  sessionKey?: string;
  requestId?: string;
}): boolean {
  return emitPostRunMemoryEvent({
    source: "gateway-agent",
    status: params.outcome,
    sessionKey: params.sessionKey,
    requestId: params.requestId,
  });
}

export function emitReplyAgentPostRunMemory(params: {
  outcome: ReplyAgentPostRunOutcome;
  sessionKey?: string;
  agentId?: string;
  requestId?: string;
}): boolean {
  return emitPostRunMemoryEvent({
    source: "reply-agent",
    status: params.outcome,
    sessionKey: params.sessionKey,
    agentId: params.agentId,
    requestId: params.requestId,
  });
}
