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
      const cases: Case[] = await listCasesApi();
      const allEvents: Array<EscalationEvent & { caseRef?: string; caseTitle?: string }> = [];

      await Promise.all(
        cases.map(async (c: Case) => {
          try {
            const evs: EscalationEvent[] = await listCaseEscalationsApi(c.id);
            evs.forEach((ev: EscalationEvent) => {
              allEvents.push({
                ...ev,
                caseRef: c.reference_number,
                caseTitle: c.title,
              });
            });
          } catch {
            // Ignored
          }
        })
      );

      allEvents.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setEscalations(allEvents);
    } catch {
      // Handled
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-high p-4 rounded border border-outline-variant/30 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[24px]">notifications_active</span>
          <div>
            <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
              DISPATCH & ALERTS // SCHEDULER
            </span>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              Dispatch Alerts & Human Escalation Center
            </h1>
          </div>
        </div>

        <button
          onClick={handleRunSweep}
          disabled={sweepLoading}
          className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors flex items-center gap-1.5 uppercase"
        >
          <span className="material-symbols-outlined text-[16px]">bolt</span>
          <span>{sweepLoading ? 'Running The Sweep...' : 'Trigger "The Sweep" Now'}</span>
        </button>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-12 text-center font-mono text-xs text-on-surface-variant">
            Loading dispatch feed...
          </div>
        ) : escalations.length === 0 ? (
          <div className="p-12 text-center bg-surface-container-low rounded border border-outline-variant/30 font-mono text-xs text-on-surface-variant italic">
            No active escalation events or dispatch alerts. All open cases are healthy!
          </div>
        ) : (
          escalations.map((ev) => {
            const isAcknowledged = !!ev.acknowledged_at;
            return (
              <div
                key={ev.id}
                className={`p-4 rounded border shadow-xs space-y-2 ${
                  isAcknowledged
                    ? 'bg-surface-container-lowest border-outline-variant/30 opacity-80'
                    : 'bg-red-50/70 border-error/40'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                      ev.trigger_type === 'SLA_BREACH' || ev.trigger_type === 'MANUAL_OPERATOR'
                        ? 'bg-error text-on-error'
                        : 'bg-secondary text-on-secondary'
                    }`}>
                      [{ev.trigger_type}]
                    </span>
                    <span className="font-bold text-primary">#{ev.caseRef}</span>
                    <span className="text-on-surface font-headline font-semibold text-sm">
                      {ev.caseTitle}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-on-surface-variant text-[11px]">
                      {new Date(ev.created_at).toLocaleString()}
                    </span>
                    {!isAcknowledged ? (
                      <button
                        onClick={() => handleAcknowledge(ev.id)}
                        className="px-3 py-1 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs"
                      >
                        Acknowledge
                      </button>
                    ) : (
                      <span className="px-2 py-0.5 bg-surface-container text-primary rounded font-mono text-[10px] font-bold">
                        ✓ Acknowledged
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-on-surface font-sans leading-relaxed">
                  {ev.reason}
                </p>

                <div className="text-[11px] font-mono text-on-surface-variant pt-1 border-t border-outline-variant/20 flex items-center gap-4">
                  <span>Target Role: <strong>{ev.notified_role}</strong></span>
                  {ev.acknowledged_at && (
                    <span>Acknowledged At: {new Date(ev.acknowledged_at).toLocaleTimeString()}</span>
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
