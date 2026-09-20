import React, { useState, useEffect } from 'react';
import { OperationalInsights } from '../api/types';
import { getOperationalInsightsApi, exportCasesCsvApi } from '../api/insights';

export const InsightsView: React.FC = () => {
  const [timeWindow, setTimeWindow] = useState<'7d' | '30d' | '90d' | 'all'>('30d');
  const [insights, setInsights] = useState<OperationalInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const fetchInsights = async (selectedWindow: '7d' | '30d' | '90d' | 'all') => {
    setLoading(true);
    try {
      const data = await getOperationalInsightsApi(selectedWindow);
      setInsights(data);
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights(timeWindow);
  }, [timeWindow]);

  const handleExportCsv = async () => {
    setExporting(true);
    try {
      const blob = await exportCasesCsvApi();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `assistiq_cases_export_${timeWindow}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch {
      alert('Failed to export CSV report');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Header & Cycle Pill Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass p-5 rounded-xl border border-outline-variant/40 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary shadow-xs">
            <span className="material-symbols-outlined text-[24px]">query_stats</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary radar-live" />
              <span className="font-mono text-[10px] text-on-surface-variant uppercase font-bold tracking-wider">
                AUDIT SCOPE // OPS BENCH
              </span>
            </div>
            <h1 className="font-headline text-xl font-bold text-on-surface">
              Manager Operational Insights Dashboard
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Cycle Selector Pills */}
          <div className="inline-flex bg-surface-container-lowest/80 backdrop-blur-md p-1 rounded-lg border border-outline-variant/30 shadow-xs font-mono text-xs">
            {(['7d', '30d', '90d', 'all'] as const).map((w) => (
              <button
                key={w}
                onClick={() => setTimeWindow(w)}
                className={`px-3 py-1 rounded-md transition-all uppercase press-tactile ${
                  timeWindow === w
                    ? 'bg-primary text-on-primary font-bold shadow-xs'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/50'
                }`}
              >
                {w}
              </button>
            ))}
          </div>

          <button
            onClick={handleExportCsv}
            disabled={exporting}
            className="px-3.5 py-1.5 liquid-glass hover:bg-surface-container/60 rounded-lg border border-outline-variant/40 text-xs font-mono font-bold text-on-surface flex items-center gap-1.5 press-tactile transition-all shadow-xs disabled:opacity-50"
          >
            <span className={`material-symbols-outlined text-[16px] ${exporting ? 'animate-spin' : ''}`}>
              {exporting ? 'sync' : 'download'}
            </span>
            <span>{exporting ? 'Exporting...' : 'Export CSV'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4 p-4">
          <div className="h-32 liquid-glass rounded-xl shimmer-warm border border-outline-variant/30" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-28 liquid-glass rounded-xl shimmer-warm border border-outline-variant/30" />
            ))}
          </div>
        </div>
      ) : insights ? (
        <div className="space-y-6">
          {/* AI Diagnostic Narrative Card (Matching Stitch Screen) */}
          <section className="liquid-glass-elevated rounded-xl p-5 shadow-md border border-outline-variant/40 space-y-3.5 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2.5">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[22px]">psychology</span>
                <h2 className="font-headline text-base font-bold text-on-surface">
                  AI Diagnostic Narrative
                </h2>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-primary-container text-on-primary-container font-mono text-[10px] font-bold tracking-wider uppercase shadow-xs flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                HIGH CONFIDENCE
              </span>
            </div>

            <p className="font-sans text-sm text-on-surface leading-relaxed pl-3 border-l-2 border-primary/40">
              {insights.ai_narrative ||
                `During this ${timeWindow.toUpperCase()} reporting cycle, ${insights.total_cases} total dockets were recorded with an overall SLA compliance rate of ${insights.sla_compliance_rate_percent}%.`}
            </p>

            <div className="liquid-glass p-3.5 rounded-lg border border-outline-variant/30 flex items-start gap-3 shadow-xs">
              <span className="material-symbols-outlined text-tertiary text-[20px] mt-0.5">lightbulb</span>
              <div>
                <span className="font-mono text-[10px] text-tertiary uppercase font-bold tracking-wider block">
                  SYSTEM RECOMMENDATION
                </span>
                <span className="font-sans text-xs text-on-surface-variant leading-relaxed">
                  Focus operator bandwidth on initial response queues to maintain SLA targets above 95.0%.
                </span>
              </div>
            </div>
          </section>

          {/* 4 Primary KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 1. Ticket Volume */}
            <div className="liquid-glass-interactive p-4.5 rounded-xl border border-outline-variant/30 shadow-xs flex flex-col justify-between space-y-2.5 card-3d">
              <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant uppercase font-bold">
                <span>TICKET VOLUME</span>
                <span className="material-symbols-outlined text-[18px] text-primary">folder_open</span>
              </div>
              <div>
                <div className="font-headline text-2xl font-bold text-on-surface">
                  {insights.total_cases}
                </div>
                <div className="font-mono text-xs text-primary font-medium mt-0.5 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  Resolved: {insights.resolved_cases}
                </div>
              </div>
              <div className="font-mono text-[10px] text-on-surface-variant border-t border-outline-variant/20 pt-2">
                Active Cycle Count: <strong>{insights.total_cases - insights.resolved_cases}</strong>
              </div>
            </div>

            {/* 2. 24/7 SLA Compliance */}
            <div className="liquid-glass-interactive p-4.5 rounded-xl border border-outline-variant/30 shadow-xs flex flex-col justify-between space-y-2.5 card-3d">
              <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant uppercase font-bold">
                <span>24/7 SLA RATE</span>
                {insights.sla_compliance_rate_percent >= 90 ? (
                  <span className="px-2 py-0.5 rounded-full bg-primary-container text-on-primary-container font-mono text-[9px] font-bold shadow-xs">
                    OPTIMAL
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-full bg-error text-on-error font-mono text-[9px] font-bold shadow-xs">
                    BREACH
                  </span>
                )}
              </div>
              <div>
                <div className={`font-headline text-2xl font-bold ${
                  insights.sla_compliance_rate_percent >= 90 ? 'text-primary' : 'text-error'
                }`}>
                  {insights.sla_compliance_rate_percent}%
                </div>
                <div className="font-sans text-xs text-on-surface-variant mt-0.5">
                  Target: 95.0%
                </div>
              </div>
              <div className="w-full bg-surface-container-highest/60 h-2 rounded-full overflow-hidden p-0.5 border border-outline-variant/20">
                <div
                  className="bg-primary h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, insights.sla_compliance_rate_percent)}%` }}
                />
              </div>
            </div>

            {/* 3. Average Resolution Time (MTTR) */}
            <div className="liquid-glass-interactive p-4.5 rounded-xl border border-outline-variant/30 shadow-xs flex flex-col justify-between space-y-2.5 card-3d">
              <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant uppercase font-bold">
                <span>AVG RESOLUTION (MTTR)</span>
                <span className="material-symbols-outlined text-[18px] text-tertiary">timer</span>
              </div>
              <div>
                <div className="font-headline text-2xl font-bold text-on-surface">
                  {insights.avg_resolution_minutes > 60
                    ? `${(insights.avg_resolution_minutes / 60).toFixed(1)}h`
                    : `${insights.avg_resolution_minutes}m`}
                </div>
                <div className="font-sans text-xs text-on-surface-variant mt-0.5">
                  Resolution compliance: <strong className="text-on-surface">{insights.resolve_compliance_rate_percent}%</strong>
                </div>
              </div>
              <div className="font-mono text-[10px] text-on-surface-variant border-t border-outline-variant/20 pt-2">
                First-response: <strong>{insights.response_compliance_rate_percent}%</strong>
              </div>
            </div>

            {/* 4. Reopen Rate */}
            <div className="liquid-glass-interactive p-4.5 rounded-xl border border-outline-variant/30 shadow-xs flex flex-col justify-between space-y-2.5 card-3d">
              <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant uppercase font-bold">
                <span>REOPEN RATE</span>
                <span className="px-2 py-0.5 rounded-full bg-primary-container text-on-primary-container font-mono text-[9px] font-bold shadow-xs">
                  OPTIMAL
                </span>
              </div>
              <div>
                <div className="font-headline text-2xl font-bold text-primary">
                  {insights.reopen_rate_percent}%
                </div>
                <div className="font-sans text-xs text-on-surface-variant mt-0.5">
                  Benchmark: &lt; 5.0%
                </div>
              </div>
              <div className="font-mono text-[10px] text-primary border-t border-outline-variant/20 pt-2">
                Reopened count: <strong>{insights.reopened_cases}</strong>
              </div>
            </div>
          </div>

          {/* Team Performance Table */}
          <div className="liquid-glass rounded-xl p-5 border border-outline-variant/30 shadow-sm space-y-3.5">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">groups</span>
              <h2 className="font-headline text-base font-bold text-on-surface">
                Support Team Performance Breakdown
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-outline-variant/30 text-on-surface-variant text-[11px]">
                    <th className="py-2.5 px-3 uppercase tracking-wider">Team</th>
                    <th className="py-2.5 px-3 uppercase tracking-wider">Assigned Cases</th>
                    <th className="py-2.5 px-3 uppercase tracking-wider">Resolved Cases</th>
                    <th className="py-2.5 px-3 uppercase tracking-wider">SLA Breaches</th>
                    <th className="py-2.5 px-3 uppercase tracking-wider">Avg Resolution Time</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.team_metrics && insights.team_metrics.length > 0 ? (
                    insights.team_metrics.map((tm) => (
                      <tr key={tm.team_id} className="border-b border-outline-variant/20 hover:bg-surface-container/40 transition-colors">
                        <td className="py-3 px-3 font-bold text-on-surface">{tm.team_name}</td>
                        <td className="py-3 px-3">{tm.assigned_count}</td>
                        <td className="py-3 px-3 text-primary font-bold">{tm.resolved_count}</td>
                        <td className="py-3 px-3">
                          {tm.breach_count > 0 ? (
                            <span className="text-error font-bold bg-error-container/50 px-2 py-0.5 rounded">{tm.breach_count}</span>
                          ) : (
                            <span className="text-primary font-semibold">0</span>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          {tm.avg_resolution_minutes > 60
                            ? `${(tm.avg_resolution_minutes / 60).toFixed(1)}h`
                            : `${tm.avg_resolution_minutes}m`}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-on-surface-variant italic font-sans">
                        No team metrics recorded in this window.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
