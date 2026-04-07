import { getDb, jsonInsert, isJsonMode } from "../db/connection.js";
import {
  decisionSchema,
  buildTool,
} from "./common.js";

interface LogDecisionParams {
  title: string;
  rationale?: string;
  alternatives?: string[];
  supersedes_id?: number;
  tags?: string[];
}

export const logDecisionTool = buildTool({
  name: "log_decision",
  description: "Record an architectural decision into SQLite",
  parameters: decisionSchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();
    const alternativesJson = params.alternatives
      ? JSON.stringify(params.alternatives)
      : null;
    const tagsJson = params.tags ? JSON.stringify(params.tags) : null;

    if (isJsonMode()) {
      const now = new Date().toISOString();
      const row = {
        title: params.title,
        rationale: params.rationale ?? null,
        alternatives: alternativesJson,
        supersedes: params.supersedes_id ?? null,
        created_at: now,
        session_key: null,
        tags: tagsJson,
      };
      const id = jsonInsert("decisions", row);
      return { id, title: params.title, created_at: now };
    }

    const stmt = db.prepare(`
      INSERT INTO decisions (title, rationale, alternatives, supersedes, session_key, tags)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      params.title,
      params.rationale ?? null,
      alternativesJson,
      params.supersedes_id ?? null,
      null,
      tagsJson
    );
    const row = db.get<{ id: number; title: string; created_at: string }>(
      "SELECT id, title, created_at FROM decisions WHERE id = ?",
      [result.id ?? result]
    );
    return row;
  },
});
