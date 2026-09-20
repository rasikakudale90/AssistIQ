import React, { useState, useEffect } from 'react';
import { listCasesApi } from '../api/cases';
import { listCaseEscalationsApi, acknowledgeEscalationApi, runTheSweepApi } from '../api/escalations';
import { Case, EscalationEvent } from '../api/types';

export const DispatchView: React.FC = () => {
  const [escalations, setEscalations] = useState<Array<EscalationEvent & { caseRef?: string; caseTitle?: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [sweepLoading, setSweepLoading] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const casesData = await listCasesApi();
      const cases: Case[] = Array.isArray(casesData) ? casesData : [];
      const allEvents: Array<EscalationEvent & { caseRef?: string; caseTitle?: string }> = [];

      await Promise.all(
        cases.map(async (c: Case) => {
          try {
            const evs: EscalationEvent[] = await listCaseEscalationsApi(c.id);
            if (Array.isArray(evs)) {
              evs.forEach((ev: EscalationEvent) => {
                allEvents.push({
                  ...ev,
                  caseRef: c.reference_number || c.id.slice(0, 8),
                  caseTitle: c.title,
                });
              });
            }
          } catch {
            // Ignored
          }
        })
      );

      allEvents.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setEscalations(allEvents);
    } catch {
      setEscalations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleRunSweep = async () => {
    setSweepLoading(true);
    try {
      await runTheSweepApi();
      alert('The Sweep background scheduler executed successfully! Evaluated all open cases for SLA breaches & risk signals.');
      await fetchAlerts();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to trigger Sweep');
    } finally {
      setSweepLoading(false);
    }
  };

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeEscalationApi(id);
      await fetchAlerts();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to acknowledge escalation');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass p-5 rounded-xl border border-outline-variant/40 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary shadow-xs">
            <span className="material-symbols-outlined text-[24px]">notifications_active</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary radar-live" />
              <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
                DISPATCH & ALERTS // SCHEDULER
              </span>
            </div>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              Dispatch Alerts & Human Escalation Center
            </h1>
          </div>
        </div>

        <button
          onClick={handleRunSweep}
          disabled={sweepLoading}
          className="px-4 py-2.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-md press-tactile transition-all flex items-center gap-2 uppercase tracking-wider disabled:opacity-50"
        >
          <span className={`material-symbols-outlined text-[16px] ${sweepLoading ? 'animate-spin' : ''}`}>
            {sweepLoading ? 'sync' : 'bolt'}
          </span>
          <span>{sweepLoading ? 'Running The Sweep...' : 'Trigger "The Sweep" Now'}</span>
        </button>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3.5">
        {loading ? (
          <div className="p-8 space-y-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-24 liquid-glass rounded-xl shimmer-warm border border-outline-variant/30" />
            ))}
          </div>
        ) : escalations.length === 0 ? (
          <div className="p-12 text-center liquid-glass rounded-xl border border-outline-variant/30 font-mono text-xs text-on-surface-variant italic space-y-2">
            <span className="material-symbols-outlined text-secondary text-3xl block">verified_user</span>
            <span>No active escalation events or dispatch alerts. All open cases are healthy!</span>
          </div>
        ) : (
          escalations.map((ev) => {
            const isAcknowledged = ev.status === 'acknowledged' || ev.status === 'resolved' || !!ev.acknowledged_at;
            const isCritical = ev.trigger_type === 'SLA_BREACH' || ev.trigger_type === 'MISSED_DEADLINE' || ev.trigger_type === 'OPERATOR_REQUESTED';

            return (
              <div
                key={ev.id}
                className={`p-4.5 rounded-xl border shadow-xs space-y-3 card-3d transition-all ${
                  isAcknowledged
                    ? 'liquid-glass border-outline-variant/30 opacity-80'
                    : isCritical
                      ? 'bg-error-container/25 backdrop-blur-md border-error/50 shadow-red-900/5'
                      : 'liquid-glass-elevated border-secondary/40'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className={`w-2.5 h-2.5 rounded-full ${isCritical && !isAcknowledged ? 'bg-error radar-breached' : 'bg-secondary radar-live'}`} />
                    <span className={`px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px] tracking-wider shadow-xs ${
                      isCritical
                        ? 'bg-error text-on-error'
                        : 'bg-secondary text-on-secondary'
                    }`}>
                      [{ev.trigger_type || 'ALERT'}]
                    </span>
                    <span className="font-bold text-primary">#{ev.caseRef}</span>
                    <span className="text-on-surface font-headline font-bold text-sm">
                      {ev.caseTitle}
                    </span>
                  </div>

                  <div className="flex items-center gap-2.5">
                    <span className="text-on-surface-variant text-[11px] bg-surface-container-low/70 px-2 py-0.5 rounded border border-outline-variant/20">
                      {new Date(ev.created_at).toLocaleString()}
                    </span>
                    {!isAcknowledged ? (
                      <button
                        onClick={() => handleAcknowledge(ev.id)}
                        className="px-3.5 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-sm press-tactile transition-all"
                      >
                        Acknowledge
                      </button>
                    ) : (
                      <span className="px-2.5 py-1 bg-surface-container/80 text-primary rounded-full font-mono text-[10px] font-bold border border-outline-variant/30 flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">check_circle</span>
                        Acknowledged
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-on-surface font-sans leading-relaxed pl-4 border-l-2 border-outline-variant/40">
                  {ev.reason}
                </p>

                <div className="text-[11px] font-mono text-on-surface-variant pt-2 border-t border-outline-variant/20 flex items-center justify-between flex-wrap gap-2">
                  <span>Target Role: <strong className="text-on-surface">{ev.notified_role || 'TeamLead / Manager'}</strong></span>
                  {ev.acknowledged_at && (
                    <span>Acknowledged At: <strong className="text-on-surface">{new Date(ev.acknowledged_at).toLocaleTimeString()}</strong></span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
