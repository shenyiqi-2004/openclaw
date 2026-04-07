/**
 * src/plugin/index.ts
 * Core registration logic for the openclaw-security plugin.
 */
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { createExecSecurityCheckTool } from "../tools/exec-security-check.js";
import { createPermissionCheckTool } from "../tools/permission-check.js";
import { runSecurityCheck } from "../tools/exec-security-check.js";

/** Re-export for convenience */
export { runSecurityCheck } from "../tools/exec-security-check.js";
export { runPermissionCheck } from "../tools/permission-check.js";

/** Derive the effective boolean config value. */
function isEnabled(pluginConfig: unknown): boolean {
  if (typeof pluginConfig === "object" && pluginConfig !== null && !Array.isArray(pluginConfig)) {
    const cfg = pluginConfig as Record<string, unknown>;
    if (typeof cfg.enabled === "boolean") return cfg.enabled;
  }
  return true; // enabled by default
}

const securityPlugin = {
  id: "openclaw-security",
  name: "OpenClaw Security",
  description:
    "Exec security validation (15-layer command check) and three-layer permission model for OpenClaw",

  register(api: OpenClawPluginApi) {
    const enabled = isEnabled(api.pluginConfig);

    if (!enabled) {
      api.logger.info("[security] Plugin disabled by configuration");
      return;
    }

    api.logger.info("[security] Registering exec_security_check and permission_check tools");

    // Register exec_security_check tool
    api.registerTool(() => createExecSecurityCheckTool());

    // Register permission_check tool
    api.registerTool(() => createPermissionCheckTool());

    // Register pre-exec hook: intercept exec tool calls and run security check
    // This hook fires before the exec tool executes, allowing us to block dangerous commands.
    // Gateway calls hookRunner.runBeforeToolCall() which dispatches to "before_tool_call" event.
    // Handler signature: (event: { toolName, params, runId?, toolCallId? }, ctx) => result | void
    const hookHandler = async (
      event: { toolName: string; params: Record<string, unknown>; runId?: string; toolCallId?: string },
      _ctx: unknown,
    ) => {
      // Only intercept exec tool
      if (event.toolName !== "exec" && event.toolName !== "ExecuteCommand") return;

      const command = event.params?.command ?? event.params?.cmd ?? event.params?.script;
      if (typeof command !== "string" || !command.trim()) return;

      const result = runSecurityCheck(command);

      if (result.blocked) {
        api.logger.warn(
          `[security] Blocked dangerous command: ${result.reason ?? result.risks.join("; ")}`,
        );
        return {
          block: true,
          blockReason: `[security] Command blocked: ${result.reason ?? result.risks.join("; ")}`,
        };
      }

      if (result.score >= 70) {
        api.logger.warn(
          `[security] High-risk command (score=${result.score}): ${result.risks.join("; ")}`,
        );
        return { requireApproval: true };
      } else {
        api.logger.debug(`[security] Command passed check (score=${result.score})`);
      }
    };

    api.registerHook(
      "before_tool_call",
      hookHandler,
      { name: "exec-security-pre-check" },
    );

    api.logger.info(
      "[security] Plugin loaded — exec_security_check and permission_check tools registered, " +
        "pre-exec hook active",
    );
  },
};

export default securityPlugin;
