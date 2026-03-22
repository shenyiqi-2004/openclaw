import type { MemoryCategory } from "../../extensions/memory-lancedb-pro/config.js";
import {
  createMemoryLanceDbProService,
  inferCategory,
  inferImportance,
  rankRecallResults,
} from "../../extensions/memory-lancedb-pro/service.js";

type BridgeCommand = "stats" | "recall" | "store" | "update" | "forget";

async function readStdinJson(): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (!text) {
    return {};
  }
  return JSON.parse(text) as Record<string, unknown>;
}

function respond(data: unknown): void {
  process.stdout.write(`${JSON.stringify(data)}\n`);
}

function readString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

async function main(): Promise<void> {
  const command = (process.argv[2] ?? "").trim() as BridgeCommand;
  const payload = await readStdinJson();
  const runtimeConfigPath =
    typeof payload.runtime_config_path === "string" && payload.runtime_config_path.trim()
      ? payload.runtime_config_path.trim()
      : undefined;
  const service = await createMemoryLanceDbProService({
    runtimeConfigPath,
    skipWarmup: true,
  });
  if (!service) {
    respond({ ok: false, reason: "memory-lancedb-pro unavailable" });
    process.exitCode = 2;
    return;
  }
  const { cfg, db, embeddings } = service;

  if (command === "stats") {
    respond({
      ok: true,
      backend: "memory_lancedb_pro",
      config: {
        dbPath: cfg.dbPath,
        recallLimit: cfg.recallLimit,
        recallMinScore: cfg.recallMinScore,
      },
      stats: await db.stats(),
    });
    return;
  }

  if (command === "recall") {
    const query = readString(payload.query);
    const limit = Math.max(1, Number(payload.limit ?? cfg.recallLimit));
    if (!query) {
      respond({ ok: false, reason: "query required" });
      process.exitCode = 2;
      return;
    }
    const vector = await embeddings.embed(query);
    const rows = await db.search(vector, Math.max(limit * 3, 6));
    const ranked = rankRecallResults(rows, cfg.recallMinScore, limit);
    respond({
      ok: true,
      backend: "memory_lancedb_pro",
      items: ranked.map((row) => ({
        id: row.entry.id,
        content: row.entry.text,
        kind: row.entry.kind,
        importance: row.entry.importance,
        created_at: row.entry.createdAt,
        score: row.score,
        combined: row.combined,
      })),
    });
    return;
  }

  if (command === "store") {
    const text = readString(payload.text);
    if (!text) {
      respond({ ok: false, reason: "text required" });
      process.exitCode = 2;
      return;
    }
    const kind = (payload.kind as MemoryCategory | undefined) ?? inferCategory(text) ?? "fact";
    const importance =
      typeof payload.importance === "number" ? payload.importance : inferImportance(kind);
    const vector = await embeddings.embed(text);
    const duplicates = await db.search(vector, 1);
    const duplicate = rankRecallResults(duplicates, cfg.duplicateScore, 1)[0];
    if (duplicate) {
      respond({
        ok: true,
        backend: "memory_lancedb_pro",
        stored: false,
        reason: "duplicate",
        duplicate_id: duplicate.entry.id,
      });
      return;
    }
    const stored = await db.store({
      text,
      vector,
      kind,
      importance,
    });
    respond({
      ok: true,
      backend: "memory_lancedb_pro",
      stored: true,
      item: stored,
    });
    return;
  }

  if (command === "update") {
    const memoryId = readString(payload.memory_id);
    if (!memoryId) {
      respond({ ok: false, reason: "memory_id required" });
      process.exitCode = 2;
      return;
    }
    const existing = await db.getById(memoryId);
    if (!existing) {
      respond({ ok: true, backend: "memory_lancedb_pro", updated: false, reason: "not-found" });
      return;
    }
    const nextText =
      typeof payload.text === "string" && payload.text.trim() ? payload.text.trim() : existing.text;
    const nextKind = (payload.kind as MemoryCategory | undefined) ?? existing.kind;
    const nextImportance =
      typeof payload.importance === "number" ? payload.importance : existing.importance;
    const vector = nextText === existing.text ? existing.vector : await embeddings.embed(nextText);
    const updated = await db.put({
      id: existing.id,
      text: nextText,
      vector,
      kind: nextKind,
      importance: nextImportance,
      createdAt: existing.createdAt,
    });
    respond({
      ok: true,
      backend: "memory_lancedb_pro",
      updated: true,
      item: updated,
    });
    return;
  }

  if (command === "forget") {
    const memoryId = readString(payload.memory_id);
    if (!memoryId) {
      respond({ ok: false, reason: "memory_id required" });
      process.exitCode = 2;
      return;
    }
    await db.delete(memoryId);
    respond({
      ok: true,
      backend: "memory_lancedb_pro",
      deleted: true,
      memory_id: memoryId,
    });
    return;
  }

  respond({ ok: false, reason: "unknown command" });
  process.exitCode = 2;
}

void main().catch((error) => {
  respond({ ok: false, reason: String(error) });
  process.exitCode = 1;
});
