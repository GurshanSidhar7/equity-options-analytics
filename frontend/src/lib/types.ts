export interface HistoryPoint {
  date: string;
  close: number | null;
  adjusted_close: number | null;
  log_return: number | null;
  hv20: number | null;
  hv30: number | null;
}

export interface Overview {
  ticker: string;
  currency: string | null;
  source: string;
  timestamp: string;
  as_of: string;
  spot: number | null;
  spot_basis: string;
  daily_change: number | null;
  daily_change_pct: number | null;
  hv20: number | null;
  hv30: number | null;
  periods_per_year: number;
  volatility_basis: string;
  units: string;
  history: HistoryPoint[];
  warnings: string[];
  desk_translator: OverviewExplanation | null;
}

export interface ExplanationValue {
  label: string;
  value: number | null;
  unit: string;
}

export interface ExplanationItem {
  id: string;
  title: string;
  plain_english: string;
  why_it_matters: string;
  math_expression: string;
  numerical_example: string;
  technical_note: string;
  values: ExplanationValue[];
}

export interface OverviewExplanation {
  items: ExplanationItem[];
  comparison: {
    hv20: number | null;
    hv30: number | null;
    absolute_difference_pp: number | null;
    relationship: "above" | "below" | "equal" | "unavailable";
  };
}

export interface PricingExplanation {
  items: ExplanationItem[];
  scenarios: {
    spot_strike_pct: number;
    spot_relationship: "above" | "below" | "equal";
    spot_move: number;
    delta_model_change: number | null;
    approx_delta_after_up_1: number | null;
    volatility_before: number;
    volatility_after: number;
    vega_model_change: number | null;
    elapsed_calendar_days: number;
    theta_model_change: number | null;
  };
  sensitivity_check: {
    current_model_price: number;
    repriced_model_price: number;
    actual_model_change: number;
    delta_only_estimate: number;
    delta_gamma_estimate: number;
  } | null;
}

export interface GreekValues {
  delta: number | null;
  gamma: number | null;
  vega_per_vol_point: number | null;
  theta_per_day: number | null;
}

export interface GreekCurvePoint extends GreekValues {
  spot: number;
}

export interface PricingResult {
  option_type: "call" | "put";
  spot: number;
  model_price: number;
  intrinsic_value: number;
  time_value: number;
  time_to_expiry_years: number;
  units: string;
  model: string;
  greeks: GreekValues;
  greek_curve: GreekCurvePoint[];
  greek_units: string;
  desk_translator: PricingExplanation;
}

export interface NewsArticle {
  title: string;
  source: string;
  published_at: string;
  url: string;
  summary: string | null;
  topics: string[];
  provider_sentiment: { label: string; score: number | null } | null;
  why_it_may_matter: string | null;
  match_reason: string;
}

export interface NewsResponse {
  ticker: string;
  retrieved_at: string;
  status: "ok" | "empty" | "not_configured" | "unavailable" | "rate_limited";
  message: string | null;
  articles: NewsArticle[];
  provider: string;
  cache_ttl_seconds: number;
  selection_note: string;
}
