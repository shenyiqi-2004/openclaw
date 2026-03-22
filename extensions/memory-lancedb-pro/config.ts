import { homedir } from "node:os";
import { join } from "node:path";

export const MEMORY_CATEGORIES = [
  "preference",
  "workflow",
  "fact",
  "failure_fix",
  "constraint",
] as const;

export type MemoryCategory = (typeof MEMORY_CATEGORIES)[number];

export type MemoryLanceDbProConfig = {
  embedding: {
    apiKey: string;
    model: string;
    baseUrl?: string;
    dimensions?: number;
  };
  dbPath: string;
  autoRecall: boolean;
  autoCapture: boolean;
  recallLimit: number;
  recallMinScore: number;
  recallMaxChars: number;
  persistMaxPerTurn: number;
  duplicateScore: number;
  enableManagementTools: boolean;
};

const DEFAULT_MODEL = "qwen3-embedding:4b";
const DEFAULT_DB_PATH = join(homedir(), ".openclaw", "memory", "lancedb-pro");
const DEFAULT_RECALL_LIMIT = 3;
const DEFAULT_RECALL_MIN_SCORE = 0.72;
const DEFAULT_RECALL_MAX_CHARS = 700;
const DEFAULT_PERSIST_MAX_PER_TURN = 2;
const DEFAULT_DUPLICATE_SCORE = 0.94;
const MODEL_DIMS: Record<string, number> = {
  "text-embedding-3-small": 1536,
  "text-embedding-3-large": 3072,
  "qwen3-embedding:4b": 2560,
};

function requireObject(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${label} required`);
  }
  return value as Record<string, unknown>;
}

function resolveEnvVarsSoft(value: string): string {
  return value.replace(/\$\{([^}]+)\}/g, (_, envVar) => {
    const envValue = process.env[envVar];
    if (!envValue) {
      return `\${${envVar}}`;
    }
    return envValue;
  });
}

function resolvePathLike(value: string): string {
  const withEnv = resolveEnvVarsSoft(value.trim());
  if (withEnv === "~") {
    return homedir();
  }
  if (withEnv.startsWith("~/")) {
    return join(homedir(), withEnv.slice(2));
  }
  return withEnv;
}

function clampInt(value: unknown, fallback: number, min: number, max: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return fallback;
  }
  return Math.min(max, Math.max(min, Math.floor(value)));
}

function clampFloat(value: unknown, fallback: number, min: number, max: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return fallback;
  }
  return Math.min(max, Math.max(min, value));
}

export function vectorDimsForModel(model: string): number {
  const dims = MODEL_DIMS[model];
  if (!dims) {
    throw new Error(`Unsupported embedding model: ${model}`);
  }
  return dims;
}

export const memoryLanceDbProConfigSchema = {
  parse(value: unknown): MemoryLanceDbProConfig {
    const cfg = requireObject(value, "memory-lancedb-pro config");
    const embedding = requireObject(cfg.embedding, "embedding");
    if (typeof embedding.apiKey !== "string" || !embedding.apiKey.trim()) {
      throw new Error("embedding.apiKey is required");
    }
    const model =
      typeof embedding.model === "string" && embedding.model.trim()
        ? embedding.model.trim()
        : DEFAULT_MODEL;
    const dimensions =
      typeof embedding.dimensions === "number" ? Math.floor(embedding.dimensions) : undefined;
    if (!dimensions) {
      vectorDimsForModel(model);
    }
    return {
      embedding: {
        apiKey: resolveEnvVarsSoft(embedding.apiKey.trim()),
        model,
        baseUrl:
          typeof embedding.baseUrl === "string" && embedding.baseUrl.trim()
            ? resolveEnvVarsSoft(embedding.baseUrl.trim())
            : undefined,
        dimensions,
      },
      dbPath:
        typeof cfg.dbPath === "string" && cfg.dbPath.trim()
          ? resolvePathLike(cfg.dbPath)
          : DEFAULT_DB_PATH,
      autoRecall: cfg.autoRecall !== false,
      autoCapture: cfg.autoCapture !== false,
      recallLimit: clampInt(cfg.recallLimit, DEFAULT_RECALL_LIMIT, 1, 5),
      recallMinScore: clampFloat(cfg.recallMinScore, DEFAULT_RECALL_MIN_SCORE, 0.3, 0.99),
      recallMaxChars: clampInt(cfg.recallMaxChars, DEFAULT_RECALL_MAX_CHARS, 200, 2000),
      persistMaxPerTurn: clampInt(cfg.persistMaxPerTurn, DEFAULT_PERSIST_MAX_PER_TURN, 1, 5),
      duplicateScore: clampFloat(cfg.duplicateScore, DEFAULT_DUPLICATE_SCORE, 0.8, 0.999),
      enableManagementTools: cfg.enableManagementTools === true,
    };
  },
};
