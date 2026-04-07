import { getDb, isJsonMode } from "../db/connection.js";
import {
  queryDecisionsSchema,
  buildTool,
} from "./common.js";

interface QueryDecisionsParams {
  limit?: number;
  tags?: string[];
  search?: string;
}

export const queryDecisionsTool = buildTool({
  name: "query_decisions",
  description: "Query architectural decisions from the governance log",
  parameters: queryDecisionsSchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();
    const limit = (params.limit as number) ?? 10;
    const search = typeof params.search === 'string' ? params.search : undefined;
    const tags = Array.isArray(params.tags) ? params.tags as string[] : undefined;

    if (isJsonMode()) {
      let rows = (db as unknown as { all: (sql: string) => unknown[] }).all(
        `SELECT * FROM decisions LIMIT ${limit}`
      ) as Array<Record<string, unknown>>;
      if (tags && tags.length > 0) {
        rows = rows.filter((r) => {
          if (!r.tags) return false;
          try {
            const rowTags = JSON.parse(r.tags as string) as string[];
            return tags!.some((t) => rowTags.includes(t));
          } catch {
            return false;
          }
        });
      }
      if (search) {
        const q = search.toLowerCase();
        rows = rows.filter((r) =>
          String(r.title ?? "").toLowerCase().includes(q) ||
          String(r.rationale ?? "").toLowerCase().includes(q)
        );
      }
      return rows.map((r) => ({
        ...r,
        alternatives: r.alternatives ? JSON.parse(r.alternatives as string) : null,
        tags: r.tags ? JSON.parse(r.tags as string) : null,
      }));
    }

    let sql = "SELECT * FROM decisions";
    const queryParams: unknown[] = [];
    const conditions: string[] = [];

    if (tags && tags.length > 0) {
      conditions.push(`tags IS NOT NULL`);
    }
    if (search) {
      conditions.push(`(title LIKE ? OR rationale LIKE ?)`);
      const q = `%${search}%`;
      queryParams.push(q, q);
    }

    if (conditions.length > 0) {
      sql += ` WHERE ${conditions.join(" AND ")}`;
    }
    sql += ` ORDER BY id DESC LIMIT ?`;
    queryParams.push(limit);

    const rows = db.all<Record<string, unknown>>(sql, queryParams);

    let results = rows.map((r) => ({
      ...r,
      alternatives: r.alternatives ? JSON.parse(r.alternatives as string) : null,
      tags: r.tags ? JSON.parse(r.tags as string) : null,
    }));

    if (tags && tags.length > 0) {
      results = results.filter((r) => {
        if (!r.tags) return false;
        return (r.tags as string[]).some((t) => tags!.includes(t));
      });
    }

    return results;
  },
});
