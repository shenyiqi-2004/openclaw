import type { DbHandle } from "./connection.js";

export function initSchema(db: DbHandle): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS decisions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      rationale TEXT,
      alternatives TEXT,
      supersedes INTEGER,
      created_at TEXT DEFAULT (datetime('now')),
      session_key TEXT,
      tags TEXT
    );
  `);

  db.exec(`
    CREATE TABLE IF NOT EXISTS governance_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL,
      payload TEXT,
      severity TEXT DEFAULT 'info',
      resolved_at TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      session_key TEXT
    );
  `);

  db.exec(`
    CREATE TABLE IF NOT EXISTS tool_stats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tool_name TEXT NOT NULL,
      duration_ms INTEGER,
      success INTEGER,
      error_message TEXT,
      session_key TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
  `);
}
