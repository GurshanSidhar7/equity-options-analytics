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
}
