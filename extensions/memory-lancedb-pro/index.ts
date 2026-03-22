import type { OpenClawPluginApi } from "openclaw/plugin-sdk/memory-lancedb";
import { memoryLanceDbProConfigSchema } from "./config.js";
import {
  createMemoryLanceDbProServiceFromConfig,
  extractPersistCandidates,
  formatRelevantMemoriesContext,
  hasUsableApiKey,
  rankRecallResults,
  shouldRecall,
  shouldRetryEmbeddingError,
} from "./service.js";

export const __testing = {
  shouldRecall,
  extractPersistCandidates,
  rankRecallResults,
  formatRelevantMemoriesContext,
  shouldRetryEmbeddingError,
};

const plugin = {
  register(api: OpenClawPluginApi): void {
    void (async () => {
      let parsedConfig;
      try {
        parsedConfig = memoryLanceDbProConfigSchema.parse(api.pluginConfig ?? {});
      } catch (error) {
        api.logger.warn(`memory-lancedb-pro: invalid plugin config, disabled: ${String(error)}`);
        return;
      }
      if (!hasUsableApiKey(parsedConfig.embedding.apiKey)) {
        api.logger.warn(
          "memory-lancedb-pro: safe-disabled mode until a real embedding API key is configured",
        );
        return;
      }

      const service = await createMemoryLanceDbProServiceFromConfig(parsedConfig, {
        skipWarmup: false,
      });
      if (!service) {
        api.logger.warn(
          "memory-lancedb-pro: safe-disabled mode until the runtime config and embedding API key are usable",
        );
        return;
      }

      const { cfg, db, embeddings } = service;

      if (cfg.autoRecall) {
        api.on("before_prompt_build", async (event) => {
          if (!shouldRecall(event.prompt ?? "", event.messages)) {
            return;
          }
          try {
            const vector = await embeddings.embed(event.prompt ?? "");
            const rows = await db.search(vector, Math.max(cfg.recallLimit * 3, 6));
            const ranked = rankRecallResults(rows, cfg.recallMinScore, cfg.recallLimit);
            if (ranked.length === 0) {
              return;
            }
            return {
              prependContext: formatRelevantMemoriesContext(ranked, cfg.recallMaxChars),
            };
          } catch (error) {
            api.logger.warn(`memory-lancedb-pro: recall failed: ${String(error)}`);
            return;
          }
        });
      }

      if (cfg.autoCapture) {
        api.on("agent_end", async (event) => {
          if (!event.success || !Array.isArray(event.messages) || event.messages.length === 0) {
            return;
          }
          try {
            const candidates = extractPersistCandidates(event.messages, cfg.persistMaxPerTurn);
            let stored = 0;
            for (const candidate of candidates) {
              const vector = await embeddings.embed(candidate.text);
              const duplicates = await db.search(vector, 1);
              const duplicate = rankRecallResults(duplicates, cfg.duplicateScore, 1)[0];
              if (duplicate) {
                continue;
              }
              await db.store({
                text: candidate.text,
                vector,
                kind: candidate.kind,
                importance: candidate.importance,
              });
              stored += 1;
            }
            if (stored > 0) {
              api.logger.info?.(`memory-lancedb-pro: stored ${stored} durable memories`);
            }
          } catch (error) {
            api.logger.warn(`memory-lancedb-pro: capture failed: ${String(error)}`);
          }
        });
      }

      if (cfg.enableManagementTools) {
        api.logger.info?.(
          "memory-lancedb-pro: management tools intentionally omitted in minimal mode",
        );
      }
    })().catch((error) => {
      api.logger.warn(`memory-lancedb-pro: initialization failed: ${String(error)}`);
    });
  },
};

export default plugin;
