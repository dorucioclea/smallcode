// SmallCode — Token & Cost Tracking
// Estimate token usage from API responses, track cost per session
// Adapted from OpenCode's getUsage pattern (simplified)

/**
 * Extract token usage from an OpenAI-compatible API response.
 */
function extractUsage(response) {
  const usage = response?.usage || {};
  return {
    inputTokens: usage.prompt_tokens || 0,
    outputTokens: usage.completion_tokens || 0,
    totalTokens: usage.total_tokens || (usage.prompt_tokens || 0) + (usage.completion_tokens || 0),
  };
}

/**
 * Estimate token count from a string (rough: 1 token ≈ 4 chars)
 */
function estimateTokens(text) {
  if (!text) return 0;
  return Math.ceil(text.length / 4);
}

/**
 * Calculate cost in USD based on model pricing.
 * Pricing is per 1M tokens.
 */
function calculateCost(usage, pricing) {
  if (!pricing) return 0;
  const inputCost = (usage.inputTokens * (pricing.input || 0)) / 1_000_000;
  const outputCost = (usage.outputTokens * (pricing.output || 0)) / 1_000_000;
  return inputCost + outputCost;
}

// Known model pricing (per 1M tokens, USD)
const MODEL_PRICING = {
  // Local models — free
  'default': { input: 0, output: 0 },

  // Escalation models (cloud)
  'claude-sonnet-4-5': { input: 3, output: 15 },
  'claude-sonnet-4-6': { input: 3, output: 15 },
  'claude-haiku-4-5': { input: 0.25, output: 1.25 },
  'gpt-5.4-mini': { input: 0.4, output: 1.6 },
  'gpt-5.4-nano': { input: 0.1, output: 0.4 },
  'deepseek-v4': { input: 0.14, output: 0.28 },
  'deepseek-v4-pro': { input: 0.5, output: 1.0 },
  'deepseek-v4-flash': { input: 0.07, output: 0.14 },
};

/**
 * Get pricing for a model (falls back to free/local)
 */
function getPricing(modelName) {
  return MODEL_PRICING[modelName] || MODEL_PRICING['default'];
}

/**
 * Session-level token tracker
 */
class TokenTracker {
  constructor() {
    this.input = 0;
    this.output = 0;
    this.total = 0;
    this.cost = 0;    // USD
    this.calls = 0;   // number of LLM calls
  }

  // Record usage from an API response
  record(response, modelName) {
    const usage = extractUsage(response);
    this.input += usage.inputTokens;
    this.output += usage.outputTokens;
    this.total += usage.totalTokens;
    this.cost += calculateCost(usage, getPricing(modelName));
    this.calls++;
  }

  // Get formatted stats for status bar
  formatShort() {
    if (this.total === 0) return '';
    const k = (n) => n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
    const costStr = this.cost > 0 ? ` $${this.cost.toFixed(4)}` : '';
    return `${k(this.total)} tokens${costStr}`;
  }

  // Get full stats
  stats() {
    return {
      input: this.input,
      output: this.output,
      total: this.total,
      cost: this.cost,
      calls: this.calls,
    };
  }
}

module.exports = { extractUsage, estimateTokens, calculateCost, getPricing, TokenTracker, MODEL_PRICING };
