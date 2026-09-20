import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Case, CasePriority, CaseStatus, CaseSummary, RiskAssessment, SLAInfo, AuditLog, AITriageResult } from '../../api/types';
import { updateCaseStatusApi, updateCasePriorityApi, getCaseTimelineApi, getSimilarCasesApi, reopenCaseApi } from '../../api/cases';
import { getCaseSummaryApi, getCaseRiskApi, getCaseTriageApi } from '../../api/ai';
import { getCaseSLAApi, createManualEscalationApi } from '../../api/escalations';
import { MessageThread } from './MessageThread';

interface CaseDetailProps {
  caseItem: Case;
  onCaseUpdated: (updatedCase: Case) => void;
}

export const CaseDetail: React.FC<CaseDetailProps> = ({ caseItem, onCaseUpdated }) => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<CaseSummary | null>(null);
  const [triage, setTriage] = useState<AITriageResult | null>(null);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [sla, setSla] = useState<SLAInfo | null>(null);
  const [similarCases, setSimilarCases] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<'messages' | 'summary' | 'triage' | 'timeline'>('messages');

  // Escalation & Reopen modals
  const [escalateOpen, setEscalateOpen] = useState(false);
  const [escalateReason, setEscalateReason] = useState('');
  const [reopenOpen, setReopenOpen] = useState(false);
  const [reopenReason, setReopenReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const isStaff = user && user.role !== 'Requester';

  const loadCaseMetadata = async () => {
    try {
      const [sumData, slaData, triageData] = await Promise.all([
        getCaseSummaryApi(caseItem.id).catch(() => null),
        getCaseSLAApi(caseItem.id).catch(() => null),
        getCaseTriageApi(caseItem.id).catch(() => null),
      ]);
      setSummary(sumData);
      setSla(slaData);
      setTriage(triageData);

      if (isStaff) {
        const [riskData, similarData] = await Promise.all([
          getCaseRiskApi(caseItem.id).catch(() => null),
          getSimilarCasesApi(caseItem.id).catch(() => []),
        ]);
        setRisk(riskData);
        setSimilarCases(similarData);
      }
    } catch {
      // Ignored
    }
  };

  useEffect(() => {
    loadCaseMetadata();
  }, [caseItem.id]);

  const handleStatusChange = async (newStatus: CaseStatus) => {
    setActionLoading(true);
    try {
      const updated = await updateCaseStatusApi(caseItem.id, newStatus, caseItem.version);
      onCaseUpdated(updated);
      await loadCaseMetadata();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Status transition failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handlePriorityChange = async (newPriority: CasePriority) => {
    setActionLoading(true);
    try {
      const updated = await updateCasePriorityApi(caseItem.id, newPriority, caseItem.version);
      onCaseUpdated(updated);
      await loadCaseMetadata();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Priority change failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEscalate = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await createManualEscalationApi(caseItem.id, escalateReason);
      setEscalateOpen(false);
      setEscalateReason('');
      alert('Level 2 Escalation event successfully broadcasted to Team Lead & Manager.');
    } catch (err: any) {
      alert(err.response?.data?.message || 'Escalation failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReopen = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      const updated = await reopenCaseApi(caseItem.id, reopenReason);
      setReopenOpen(false);
      setReopenReason('');
      onCaseUpdated(updated);
      await loadCaseMetadata();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Reopen failed');
    } finally {
      setActionLoading(false);
    }
  };

  const loadTimeline = async () => {
    try {
      const data = await getCaseTimelineApi(caseItem.id);
      setTimeline(data);
    } catch {
      // Handled
    }
  };

  const priorityColors: Record<CasePriority, string> = {
    P1: 'bg-error text-on-error',
    P2: 'bg-secondary text-on-secondary',
    P3: 'bg-tertiary-container text-on-tertiary-container',
    P4: 'bg-surface-container-high text-on-surface-variant',
  };

  return (
    <div className="bg-surface-container-high rounded-lg p-5 border border-outline-variant/30 space-y-5 shadow-sm">
      {/* Top Header Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-lowest p-4 rounded border border-outline-variant/30 shadow-xs">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold text-primary">
              #{caseItem.reference_number}
            </span>
            {isStaff ? (
              <select
                value={caseItem.priority}
                onChange={(e) => handlePriorityChange(e.target.value as CasePriority)}
                disabled={actionLoading}
                className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold cursor-pointer ${priorityColors[caseItem.priority]}`}
              >
                <option value="P1" className="bg-surface text-on-surface">P1</option>
                <option value="P2" className="bg-surface text-on-surface">P2</option>
                <option value="P3" className="bg-surface text-on-surface">P3</option>
                <option value="P4" className="bg-surface text-on-surface">P4</option>
              </select>
            ) : (
              <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${priorityColors[caseItem.priority]}`}>
                [{caseItem.priority}]
              </span>
            )}
            <span className="px-2 py-0.5 rounded bg-primary-fixed text-on-primary-fixed font-mono text-[10px] font-bold uppercase">
              {caseItem.status}
            </span>
            {caseItem.site && (
              <span className="font-mono text-[11px] text-on-surface-variant">
                📍 {caseItem.site}
              </span>
            )}
          </div>
          <h2 className="font-headline text-lg font-bold text-on-surface">
            {caseItem.title}
          </h2>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {isStaff && caseItem.status === 'New' && (
            <button
              onClick={() => handleStatusChange('InAssessment')}
              disabled={actionLoading}
              className="px-3 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs"
            >
              Start Assessment
            </button>
          )}

          {isStaff && ['InAssessment', 'New'].includes(caseItem.status) && (
            <button
              onClick={() => handleStatusChange('Assigned')}
              disabled={actionLoading}
              className="px-3 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs"
            >
              Assign Case
            </button>
          )}

          {isStaff && caseItem.status === 'Assigned' && (
            <button
              onClick={() => handleStatusChange('Resolved')}
              disabled={actionLoading}
              className="px-3 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs"
            >
              Mark Resolved
            </button>
          )}

          {caseItem.status === 'Resolved' && (
            <button
              onClick={() => handleStatusChange('Closed')}
              disabled={actionLoading}
              className="px-3 py-1.5 bg-surface-container hover:bg-surface-container-highest text-on-surface font-mono text-xs font-bold rounded"
            >
              Close Case
            </button>
          )}

          {caseItem.status === 'Closed' && (
            <button
              onClick={() => setReopenOpen(true)}
              className="px-3 py-1.5 bg-secondary text-on-secondary font-mono text-xs font-bold rounded"
            >
              Reopen (7-Day Window)
            </button>
          )}

          {isStaff && (
            <button
              onClick={() => setEscalateOpen(true)}
              className="px-3 py-1.5 bg-error/10 hover:bg-error/20 text-error font-mono text-xs font-bold rounded border border-error/30 flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[14px]">warning</span>
              Escalate L2
            </button>
          )}
        </div>
      </div>

      {/* 24/7 SLA Countdown & Risk Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/30 flex flex-col justify-between">
          <span className="text-on-surface-variant text-[10px] uppercase font-semibold">
            First Response SLA
          </span>
          <div className="mt-1">
            {sla?.first_response_at ? (
              <span className="text-primary font-bold">✓ Met First Response</span>
            ) : sla?.response_breached ? (
              <span className="text-error font-bold">⚠ RESPONSE BREACHED</span>
            ) : (
              <span className="text-on-surface font-bold">
                {sla?.minutes_to_response_deadline ? `${sla.minutes_to_response_deadline}m remaining` : 'Active'}
              </span>
            )}
          </div>
        </div>

        <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/30 flex flex-col justify-between">
          <span className="text-on-surface-variant text-[10px] uppercase font-semibold">
            Resolve Target SLA
          </span>
          <div className="mt-1">
            {sla?.resolved_at ? (
              <span className="text-primary font-bold">✓ Case Resolved</span>
            ) : sla?.resolve_breached ? (
              <span className="text-error font-bold">⚠ RESOLVE BREACHED</span>
            ) : (
              <span className="text-on-surface font-bold">
                {sla?.minutes_to_resolve_deadline ? `${Math.round(sla.minutes_to_resolve_deadline / 60)}h remaining` : 'Active'}
              </span>
            )}
          </div>
        </div>

        {risk && (
          <div className={`p-3 rounded border flex flex-col justify-between ${
            risk.risk_level === 'Critical' || risk.risk_level === 'High'
              ? 'bg-red-50 border-error/30 text-error'
              : 'bg-surface-container-lowest border-outline-variant/30 text-on-surface'
          }`}>
            <span className="text-[10px] uppercase font-semibold">
              Sweep Risk Assessment
            </span>
            <div className="mt-1 font-bold">
              [{risk.risk_level}] — Score: {risk.risk_score}
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-outline-variant/30 pb-2 text-xs font-mono">
        <button
          onClick={() => setActiveTab('messages')}
          className={`px-3 py-1 rounded transition-colors ${
            activeTab === 'messages'
              ? 'bg-primary text-on-primary font-bold'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          Message Thread
        </button>
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-3 py-1 rounded transition-colors ${
            activeTab === 'summary'
              ? 'bg-primary text-on-primary font-bold'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          AI Case Summary
        </button>
        <button
          onClick={() => setActiveTab('triage')}
          className={`px-3 py-1 rounded transition-colors ${
            activeTab === 'triage'
              ? 'bg-primary text-on-primary font-bold'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          AI Triage & Telemetry
        </button>
        <button
          onClick={() => {
            setActiveTab('timeline');
            loadTimeline();
          }}
          className={`px-3 py-1 rounded transition-colors ${
            activeTab === 'timeline'
              ? 'bg-primary text-on-primary font-bold'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          Audit Timeline
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'messages' && (
        <MessageThread caseId={caseItem.id} onMessageSent={loadCaseMetadata} />
      )}

      {activeTab === 'summary' && (
        <div className="space-y-3 bg-surface-container-lowest p-4 rounded border border-outline-variant/30">
          <div className="flex items-center gap-1.5 text-primary font-mono text-xs font-bold uppercase">
            <span className="material-symbols-outlined text-[18px]">summarize</span>
            4-Part Structured AI Case Summary (SRS §5.5)
          </div>
          {summary ? (
            <div className="space-y-2 text-xs">
              <div className="p-2.5 bg-surface-container-low rounded">
                <strong className="block text-primary font-mono text-[10px] uppercase mb-0.5">
                  1. What Was Reported
                </strong>
                <p className="text-on-surface">{summary.what_was_reported}</p>
              </div>
              <div className="p-2.5 bg-surface-container-low rounded">
                <strong className="block text-primary font-mono text-[10px] uppercase mb-0.5">
                  2. What Happened Since
                </strong>
                <p className="text-on-surface">{summary.what_happened_since}</p>
              </div>
              <div className="p-2.5 bg-surface-container-low rounded">
                <strong className="block text-primary font-mono text-[10px] uppercase mb-0.5">
                  3. What is Confirmed
                </strong>
                <p className="text-on-surface">{summary.what_is_confirmed}</p>
              </div>
              <div className="p-2.5 bg-surface-container-low rounded">
                <strong className="block text-secondary font-mono text-[10px] uppercase mb-0.5">
                  4. What Remains Unresolved
                </strong>
                <p className="text-on-surface">{summary.what_remains_unresolved}</p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant italic">No AI summary generated yet.</p>
          )}
        </div>
      )}

      {activeTab === 'triage' && (
        <div className="space-y-3 bg-surface-container-lowest p-4 rounded border border-outline-variant/30">
          <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2">
            <div className="flex items-center gap-1.5 text-primary font-mono text-xs font-bold uppercase">
              <span className="material-symbols-outlined text-[18px]">psychology</span>
              AI Triage & Diagnostic Telemetry [SRS §5.2]
            </div>
            {triage && (
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-primary-container text-on-primary-container font-semibold">
                CONFIDENCE: {triage.confidence_score !== undefined ? `${Math.round(triage.confidence_score * 100)}%` : (triage.confidence_level || 'HIGH')}
              </span>
            )}
          </div>

          {triage ? (
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-2.5 bg-surface-container-low rounded">
                  <span className="block font-mono text-[10px] text-on-surface-variant uppercase">
                    Suggested Category & Team
                  </span>
                  <strong className="text-on-surface text-sm block">
                    {triage.suggested_category || triage.predicted_category || 'General IT'}
                  </strong>
                  <span className="text-[11px] text-primary font-mono font-semibold">
                    ➔ {triage.suggested_team || 'Service Desk'}
                  </span>
                </div>

                <div className="p-2.5 bg-surface-container-low rounded">
                  <span className="block font-mono text-[10px] text-on-surface-variant uppercase">
                    Predicted Severity & Priority
                  </span>
                  <strong className="text-secondary font-mono text-sm block">
                    [{triage.suggested_priority || triage.predicted_priority || 'P3'}]
                  </strong>
                  <span className="text-[11px] text-on-surface-variant font-mono">
                    Severity: {triage.suggested_severity || 'Medium'}
                  </span>
                </div>
              </div>

              {/* Supporting Telemetry Factors */}
              {triage.supporting_factors && triage.supporting_factors.length > 0 && (
                <div className="p-3 bg-surface-container-low rounded">
                  <span className="block font-mono text-[10px] text-tertiary font-bold uppercase mb-1">
                    Supporting Telemetry & Factors
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                    {triage.supporting_factors.map((factor, i) => (
                      <li key={i}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Missing Info Clarification Questions */}
              {((triage.missing_info_questions && triage.missing_info_questions.length > 0) || (triage.missing_info && triage.missing_info.length > 0)) && (
                <div className="p-3 bg-surface-container-high rounded border-l-2 border-secondary">
                  <span className="block font-mono text-[10px] text-secondary font-bold uppercase mb-1">
                    Suggested Clarification Questions (Missing Info - SRS §5.4)
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                    {(triage.missing_info_questions || triage.missing_info || []).map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Next Action */}
              {triage.recommended_next_action && (
                <div className="p-2.5 bg-primary/5 rounded border border-primary/20 text-xs font-mono">
                  <span className="text-[10px] uppercase font-bold text-primary block">Recommended Next Action:</span>
                  <span className="text-on-surface">{triage.recommended_next_action}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant italic">No AI triage assessment recorded.</p>
          )}
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="space-y-2 max-h-[350px] overflow-y-auto">
          {timeline.length === 0 ? (
            <p className="text-xs text-on-surface-variant italic">No audit records recorded.</p>
          ) : (
            timeline.map((item) => (
              <div
                key={item.id}
                className="p-2.5 bg-surface-container-lowest rounded border border-outline-variant/30 text-xs flex items-center justify-between font-mono"
              >
                <div>
                  <span className="font-bold text-on-surface">{item.action}</span>
                  <span className="block text-[10px] text-on-surface-variant">
                    Actor: {item.actor_email || 'System'}
                  </span>
                </div>
                <span className="text-[10px] text-on-surface-variant">
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
            ))
          )}
        </div>
      )}

      {/* Candidate Similar Cases (SRS §5.7) */}
      {similarCases.length > 0 && (
        <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/30 space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-tertiary">
            <span className="material-symbols-outlined text-[16px]">content_copy</span>
            Candidate Duplicate / Similar Cases (Suggestions Only)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {similarCases.map((sc) => (
              <div key={sc.id} className="p-2 bg-surface-container-low rounded text-xs font-mono flex items-center justify-between">
                <div>
                  <span className="font-bold text-primary">#{sc.reference_number}</span>
                  <span className="block text-[11px] text-on-surface truncate">{sc.title}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 bg-tertiary-container text-on-tertiary-container rounded">
                  {Math.round(sc.similarity_score * 100)}% match
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Escalation Modal */}
      {escalateOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/60 flex items-center justify-center p-4">
          <form onSubmit={handleEscalate} className="bg-surface-container-high p-5 rounded-lg max-w-md w-full space-y-3 border border-outline-variant/40 shadow-xl">
            <h3 className="font-headline font-bold text-base text-on-surface">
              Level 2 Human Escalation Request
            </h3>
            <p className="text-xs text-on-surface-variant font-sans">
              Explicit operator request for Team Lead / Manager intervention per SRS §6.4.
            </p>
            <textarea
              required
              rows={3}
              value={escalateReason}
              onChange={(e) => setEscalateReason(e.target.value)}
              placeholder="State reason for escalation, vendor roadblock, or SLA emergency..."
              className="w-full p-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEscalateOpen(false)}
                className="px-3 py-1.5 bg-surface-container text-xs font-mono rounded"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-3 py-1.5 bg-error text-on-error text-xs font-mono font-bold rounded"
              >
                {actionLoading ? 'Broadcasting...' : 'Broadcast Escalation'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reopen Modal */}
      {reopenOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/60 flex items-center justify-center p-4">
          <form onSubmit={handleReopen} className="bg-surface-container-high p-5 rounded-lg max-w-md w-full space-y-3 border border-outline-variant/40 shadow-xl">
            <h3 className="font-headline font-bold text-base text-on-surface">
              Reopen Case (7-Day Calendar Window)
            </h3>
            <p className="text-xs text-on-surface-variant font-sans">
              Provide justification for reopening this closed docket per SRS §4.4.
            </p>
            <textarea
              required
              rows={3}
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
              placeholder="Describe recurring symptoms or incomplete resolution..."
              className="w-full p-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setReopenOpen(false)}
                className="px-3 py-1.5 bg-surface-container text-xs font-mono rounded"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-3 py-1.5 bg-secondary text-on-secondary text-xs font-mono font-bold rounded"
              >
                {actionLoading ? 'Reopening...' : 'Confirm Reopen'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
