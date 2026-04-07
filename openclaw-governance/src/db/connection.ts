import { homedir } from "os";
import { join } from "path";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";

type DbHandle = {
  run(sql: string, params?: unknown[]): void;
  get<T>(sql: string, params?: unknown[]): T | undefined;
  all<T>(sql: string, params?: unknown[]): T[];
  exec(sql: string): void;
  close(): void;
};

type JsonStore = {
  decisions: Record<string, unknown>[];
  governance_events: Record<string, unknown>[];
  tool_stats: Record<string, unknown>[];
  counters: { decisions: number; governance_events: number; tool_stats: number };
};

let db: DbHandle | null = null;
let jsonStore: JsonStore | null = null;
let useJson = false;

function getJsonPath(): string {
  const config = (globalThis as Record<string, unknown>).__openclawGovernanceConfig;
  const customPath = typeof config === "object" && config !== null && "dbPath" in config
    ? (config as Record<string, unknown>).dbPath as string
    : undefined;
  return customPath ?? join(homedir(), ".openclaw", "governance.json");
}

function getDbPath(): string {
  const config = (globalThis as Record<string, unknown>).__openclawGovernanceConfig;
  const customPath = typeof config === "object" && config !== null && "dbPath" in config
    ? (config as Record<string, unknown>).dbPath as string
    : undefined;
  return customPath ?? join(homedir(), ".openclaw", "governance.db");
}

function loadJsonStore(): JsonStore {
  const path = getJsonPath();
  if (existsSync(path)) {
    try {
      return JSON.parse(readFileSync(path, "utf-8")) as JsonStore;
    } catch {
      // corrupted, reinitialize
    }
  }
  const initial: JsonStore = {
    decisions: [],
    governance_events: [],
    tool_stats: [],
    counters: { decisions: 0, governance_events: 0, tool_stats: 0 },
  };
  const dir = join(homedir(), ".openclaw");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(path, JSON.stringify(initial, null, 2));
  return initial;
}

function saveJsonStore(): void {
  if (!jsonStore) return;
  const path = getJsonPath();
  const dir = join(homedir(), ".openclaw");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(path, JSON.stringify(jsonStore, null, 2));
}

function tryBetterSqlite3(): DbHandle | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const BetterSqlite3 = require("better-sqlite3") as {
      new(path: string): DbHandle;
    };
    const path = getDbPath();
    const dir = join(homedir(), ".openclaw");
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    return new BetterSqlite3(path);
  } catch {
    return null;
  }
}

function tryNodeSqlite(): DbHandle | null {
  try {
    // Node 22+ built-in sqlite
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const nodeSqlite = require("node:sqlite") as {
      open(path: string): Promise<DbHandle & { close(): Promise<void> }>;
    };
    return null; // async open not compatible with sync interface, skip
  } catch {
    return null;
  }
}

export function getDb(): DbHandle {
  if (db) return db;

  // Try better-sqlite3 first
  db = tryBetterSqlite3();

  if (!db) {
    // Fallback to JSON file store
    useJson = true;
    jsonStore = loadJsonStore();
    db = createJsonDbHandle();
  }

  return db;
}

function createJsonDbHandle(): DbHandle {
  const jsonDb: DbHandle = {
    run(sql: string, _params?: unknown[]) {
      // No-op for schema init
    },
    get<T>(sql: string, params?: unknown[]): T | undefined {
      if (!jsonStore) return undefined;
      const table = extractTable(sql);
      const conditions = extractConditions(sql, params as Record<string, unknown>[]);
      if (table === "decisions" && jsonStore.decisions) {
        const rows = jsonStore.decisions as Record<string, unknown>[];
        if (conditions) {
          return rows.find((r) => conditions.every((c) => r[c.key] === c.value)) as T | undefined;
        }
        return rows[rows.length - 1] as T | undefined;
      }
      if (table === "governance_events" && jsonStore.governance_events) {
        const rows = jsonStore.governance_events as Record<string, unknown>[];
        if (conditions) {
          return rows.find((r) => conditions.every((c) => r[c.key] === c.value)) as T | undefined;
        }
        return rows[rows.length - 1] as T | undefined;
      }
      if (table === "tool_stats" && jsonStore.tool_stats) {
        const rows = jsonStore.tool_stats as Record<string, unknown>[];
        if (conditions) {
          return rows.find((r) => conditions.every((c) => r[c.key] === c.value)) as T | undefined;
        }
        return rows[rows.length - 1] as T | undefined;
      }
      return undefined;
    },
    all<T>(sql: string, params?: unknown[]): T[] {
      if (!jsonStore) return [];
      const table = extractTable(sql);
      const conditions = extractConditions(sql, params as Record<string, unknown>[]);
      let rows: Record<string, unknown>[] = [];
      if (table === "decisions") rows = jsonStore.decisions ?? [];
      else if (table === "governance_events") rows = jsonStore.governance_events ?? [];
      else if (table === "tool_stats") rows = jsonStore.tool_stats ?? [];
      else return [];
      let result = rows as T[];
      if (conditions) {
        result = rows.filter((r) =>
          conditions.every((c) => r[c.key] === c.value)
        ) as T[];
      }
      // Handle ORDER BY
      if (sql.includes("ORDER BY")) {
        const match = sql.match(/ORDER BY\s+(\w+)(?:\s+(ASC|DESC))?/i);
        if (match) {
          const key = match[1];
          const desc = match[2]?.toUpperCase() === "DESC";
          result = [...result].sort((a, b) => {
            const av = (a as Record<string, unknown>)[key];
            const bv = (b as Record<string, unknown>)[key];
            if (av == null) return 1;
            if (bv == null) return -1;
            return desc ? (String(bv).localeCompare(String(av)) as number) : (String(av).localeCompare(String(bv)) as number);
          });
        }
      }
      // Handle LIMIT
      const limitMatch = sql.match(/LIMIT\s+(\d+)/i);
      if (limitMatch) {
        result = result.slice(0, parseInt(limitMatch[1], 10));
      }
      return result;
    },
    exec(_sql: string) {
      // schema already initialized via run
    },
    close() {
      if (useJson) saveJsonStore();
    },
  };
  return jsonDb;
}

function extractTable(sql: string): string {
  const match = sql.match(/FROM\s+(\w+)/i) || sql.match(/INTO\s+(\w+)/i);
  return match ? match[1] : "";
}

interface Condition { key: string; value: unknown }
function extractConditions(sql: string, params?: Record<string, unknown>[]): Condition[] | undefined {
  const whereMatch = sql.match(/WHERE\s+(.+?)(?:\s+ORDER|\s+LIMIT|\s*$)/i);
  if (!whereMatch) return undefined;
  const conditions: Condition[] = [];
  // Simple key=value extraction
  const kvMatches = whereMatch[1].matchAll(/(\w+)\s*=\s*\?/g);
  for (const m of kvMatches) {
    const key = m[1];
    const paramIndex = conditions.length;
    if (params && params[paramIndex] !== undefined) {
      conditions.push({ key, value: params[paramIndex] });
    }
  }
  return conditions.length > 0 ? conditions : undefined;
}

// JSON-mode insert helpers
export function jsonInsert(table: "decisions", row: Record<string, unknown>): number;
export function jsonInsert(table: "governance_events", row: Record<string, unknown>): number;
export function jsonInsert(table: "tool_stats", row: Record<string, unknown>): number;
export function jsonInsert(table: string, row: Record<string, unknown>): number {
  if (!jsonStore) return 0;
  if (table === "decisions") {
    jsonStore.counters.decisions++;
    const id = jsonStore.counters.decisions;
    jsonStore.decisions.push({ ...row, id });
  } else if (table === "governance_events") {
    jsonStore.counters.governance_events++;
    const id = jsonStore.counters.governance_events;
    jsonStore.governance_events.push({ ...row, id });
  } else if (table === "tool_stats") {
    jsonStore.counters.tool_stats++;
    const id = jsonStore.counters.tool_stats;
    jsonStore.tool_stats.push({ ...row, id });
  }
  saveJsonStore();
  return (jsonStore.counters as Record<string, number>)[`${table}_sequence`] as number ?? jsonStore.counters.decisions;
}

export function isJsonMode(): boolean {
  return useJson;
}
