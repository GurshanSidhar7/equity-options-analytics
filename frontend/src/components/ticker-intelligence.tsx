"use client";

import { useEffect, useState } from "react";
import type { NewsResponse } from "@/lib/types";

function timestamp(value: string) {
  return new Date(value).toLocaleString("en-GB", { timeZone: "UTC", year: "numeric", month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" }) + " UTC";
}

export function TickerIntelligence({ ticker }: { ticker: string }) {
  const [news, setNews] = useState<NewsResponse | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    let disposed = false;
    setNews(null);
    setError(false);
    async function load() {
      try {
        const response = await fetch(`/api/news?ticker=${encodeURIComponent(ticker)}`, { signal: controller.signal, cache: "no-store" });
        if (!response.ok) throw new Error("News unavailable");
        const body: NewsResponse = await response.json();
        if (!disposed) setNews(body);
      } catch {
        if (!disposed) setError(true);
      }
    }
    void load();
    return () => { disposed = true; controller.abort(); };
  }, [ticker]);
  const loading = !news && !error;
  return <section className="ticker-intelligence context-panel" aria-label={`Ticker Intelligence for ${ticker}`} aria-busy={loading}>
    <div className="context-heading"><div><p className="panel-eyebrow">COMPANY CONTEXT</p><h2>Ticker Intelligence</h2><p>Recent company coverage for {ticker}</p></div><span className="chart-chip">{ticker}</span></div>
    {news && <p className="news-selection context-note">{news.selection_note}</p>}
    {loading && <p role="status" className="news-state">Loading recent ticker news…</p>}
    {error && <p role="status" className="news-state">Recent ticker news is temporarily unavailable.</p>}
    {news && news.status !== "ok" && <p role="status" className="news-state">{news.message ?? "Recent ticker news is temporarily unavailable."}</p>}
    {news?.status === "ok" && <>
      <div className="news-grid">{news.articles.map(article => <article className="news-card" key={article.url}>
        <h3><a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a></h3>
        <p className="news-meta">{article.source} · <time dateTime={article.published_at}>{timestamp(article.published_at)}</time></p>
        <p className="news-match">{article.match_reason}</p>
        {article.summary && <p className="news-summary">{article.summary}</p>}
        {article.topics.length > 0 && <ul className="news-topics" aria-label="Provider topics">{article.topics.map(topic => <li key={topic}>{topic}</li>)}</ul>}
        {article.why_it_may_matter && <p className="context-note"><strong>Why this category may matter: </strong>{article.why_it_may_matter}</p>}
        <a className="article-link" href={article.url} target="_blank" rel="noopener noreferrer" aria-label={`Read article: ${article.title}`}>Read article <span aria-hidden="true">↗</span></a>
      </article>)}</div>
      <p className="news-retrieved">{news.provider} · Retrieved {timestamp(news.retrieved_at)}</p>
    </>}
    <p className="context-footnote">News provides context, does not establish what caused a price movement, and does not change model inputs or predict price direction. Headlines name the selected company or stock symbol. Publication selection does not independently verify article claims.</p>
  </section>;
}
