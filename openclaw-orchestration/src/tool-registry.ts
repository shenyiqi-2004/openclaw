/**
 * Tool classification registry for openclaw-orchestration.
 * Maps tool names to their safety and concurrency characteristics.
 */

export type ToolCategory = "read_only" | "mutation" | "unknown";

export interface ToolClassification {
  category: ToolCategory;
  safe_concurrent: boolean;
  max_concurrent: number;
  timeout_ms: number;
  retry_allowed: boolean;
}

/** Tools that only read data and do not modify any state. */
const READ_ONLY_TOOLS = new Set<string>([
  "read",
  "grep",
  "glob",
  "image",
  "web_search",
  "web_fetch",
  "lcm_grep",
  "lcm_describe",
  "lcm_expand",
  "lcm_expand_query",
  "tdai_memory_search",
  "tdai_conversation_search",
  "feishu_doc",
  "feishu_fetch_doc",
  "feishu_search_doc_wiki",
  "feishu_bitable_get_meta",
  "feishu_bitable_list_fields",
  "feishu_bitable_list_records",
  "feishu_bitable_get_record",
  "feishu_calendar_calendar",
  "feishu_calendar_event",
  "feishu_calendar_freebusy",
  "feishu_drive",
  "feishu_drive_file",
  "feishu_chat",
  "feishu_chat_members",
  "feishu_get_user",
  "feishu_search_user",
  "feishu_im_user_get_messages",
  "feishu_im_user_get_thread_messages",
  "feishu_im_user_search_messages",
  "feishu_task_task",
  "feishu_task_tasklist",
  "feishu_task_comment",
  "feishu_task_subtask",
  "browser",
  "canvas",
]);

/** Tools that mutate state (filesystem, network, sessions, etc.). */
const MUTATION_TOOLS = new Set<string>([
  "exec",
  "edit",
  "write",
  "browser",
  "message",
  "sessions_spawn",
  "sessions_yield",
  "process",
  "feishu_im_user_message",
  "feishu_doc",
  "feishu_update_doc",
  "feishu_create_doc",
  "feishu_doc_media",
  "feishu_doc_comments",
  "feishu_bitable_app",
  "feishu_bitable_app_table",
  "feishu_bitable_app_table_field",
  "feishu_bitable_app_table_record",
  "feishu_bitable_app_table_view",
  "feishu_bitable_create_app",
  "feishu_bitable_create_field",
  "feishu_bitable_create_record",
  "feishu_bitable_update_record",
  "feishu_calendar_event",
  "feishu_calendar_event_attendee",
  "feishu_wiki",
  "feishu_wiki_space",
  "feishu_wiki_space_node",
  "feishu_sheet",
  "feishu_task_task",
  "feishu_task_tasklist",
  "feishu_task_comment",
  "feishu_task_subtask",
  "feishu_drive_file",
  "feishu_im_bot_image",
  "feishu_im_user_fetch_resource",
  "feishu_bitable_get_meta",
  "feishu_search_user",
]);

/**
 * Get the classification for a given tool name.
 */
export function classifyTool(toolName: string): ToolClassification {
  const name = toolName.trim().toLowerCase();

  if (READ_ONLY_TOOLS.has(name)) {
    return {
      category: "read_only",
      safe_concurrent: true,
      max_concurrent: 10,
      timeout_ms: 60_000,
      retry_allowed: true,
    };
  }

  if (MUTATION_TOOLS.has(name)) {
    return {
      category: "mutation",
      safe_concurrent: false,
      max_concurrent: 1,
      timeout_ms: 120_000,
      retry_allowed: false,
    };
  }

  return {
    category: "unknown",
    safe_concurrent: false,
    max_concurrent: 1,
    timeout_ms: 60_000,
    retry_allowed: false,
  };
}

/**
 * Check if a tool is read-only.
 */
export function isReadOnlyTool(toolName: string): boolean {
  return classifyTool(toolName).category === "read_only";
}

/**
 * Check if a tool is a mutation tool.
 */
export function isMutationTool(toolName: string): boolean {
  return classifyTool(toolName).category === "mutation";
}
