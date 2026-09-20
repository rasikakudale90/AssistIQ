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
    <div className="liquid-glass rounded-xl p-6 border border-outline-variant/35 space-y-6 shadow-sm">
      {/* Top Header Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass-elevated p-4 rounded-xl border border-outline-variant/40 shadow-xs card-3d">
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
                className={`px-2.5 py-0.5 rounded-md font-mono text-[10px] font-bold cursor-pointer transition-all duration-200 press-tactile shadow-xs ${priorityColors[caseItem.priority]}`}
              >
                <option value="P1" className="bg-surface text-on-surface">P1</option>
                <option value="P2" className="bg-surface text-on-surface">P2</option>
                <option value="P3" className="bg-surface text-on-surface">P3</option>
                <option value="P4" className="bg-surface text-on-surface">P4</option>
              </select>
            ) : (
              <span className={`px-2.5 py-0.5 rounded-md font-mono text-[10px] font-bold shadow-xs ${priorityColors[caseItem.priority]}`}>
                [{caseItem.priority}]
              </span>
            )}
            <span className="px-2.5 py-0.5 rounded-md bg-primary-fixed text-on-primary-fixed font-mono text-[10px] font-bold uppercase shadow-xs">
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
              className="px-3.5 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-xs transition-all duration-200 press-tactile"
            >
              Start Assessment
            </button>
          )}

          {isStaff && ['InAssessment', 'New'].includes(caseItem.status) && (
            <button
              onClick={() => handleStatusChange('Assigned')}
              disabled={actionLoading}
              className="px-3.5 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-xs transition-all duration-200 press-tactile"
            >
              Assign Case
            </button>
          )}

          {isStaff && caseItem.status === 'Assigned' && (
            <button
              onClick={() => handleStatusChange('Resolved')}
              disabled={actionLoading}
              className="px-3.5 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-xs transition-all duration-200 press-tactile"
            >
              Mark Resolved
            </button>
          )}

          {caseItem.status === 'Resolved' && (
            <button
              onClick={() => handleStatusChange('Closed')}
              disabled={actionLoading}
              className="px-3.5 py-1.5 bg-surface-container hover:bg-surface-container-highest text-on-surface font-mono text-xs font-bold rounded-lg transition-all duration-200 press-tactile"
            >
              Close Case
            </button>
          )}

          {caseItem.status === 'Closed' && (
            <button
              onClick={() => setReopenOpen(true)}
              className="px-3.5 py-1.5 bg-secondary text-on-secondary font-mono text-xs font-bold rounded-lg transition-all duration-200 press-tactile shadow-xs"
            >
              Reopen (7-Day Window)
            </button>
          )}

          {isStaff && (
            <button
              onClick={() => setEscalateOpen(true)}
              className="px-3 py-1.5 bg-error/10 hover:bg-error/20 text-error font-mono text-xs font-bold rounded-lg border border-error/30 flex items-center gap-1.5 transition-all duration-200 press-tactile"
            >
              <span className="material-symbols-outlined text-[14px]">warning</span>
              Escalate L2
            </button>
          )}
        </div>
      </div>

      {/* 24/7 SLA Countdown & Risk Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div className="p-3.5 liquid-glass rounded-xl border border-outline-variant/35 flex flex-col justify-between card-3d">
          <span className="text-on-surface-variant text-[10px] uppercase font-bold tracking-wider">
            First Response SLA
          </span>
          <div className="mt-1.5">
            {sla?.first_response_at ? (
              <span className="text-primary font-bold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary" />
                ✓ Met First Response
              </span>
            ) : sla?.response_breached ? (
              <span className="text-error font-bold flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-error radar-breached" />
                ⚠ RESPONSE BREACHED
              </span>
            ) : (
              <span className="text-on-surface font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-primary radar-live" />
                {sla?.minutes_to_response_deadline ? `${sla.minutes_to_response_deadline}m remaining` : 'Active'}
              </span>
            )}
          </div>
        </div>

        <div className="p-3.5 liquid-glass rounded-xl border border-outline-variant/35 flex flex-col justify-between card-3d">
          <span className="text-on-surface-variant text-[10px] uppercase font-bold tracking-wider">
            Resolve Target SLA
          </span>
          <div className="mt-1.5">
            {sla?.resolved_at ? (
              <span className="text-primary font-bold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary" />
                ✓ Case Resolved
              </span>
            ) : sla?.resolve_breached ? (
              <span className="text-error font-bold flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-error radar-breached" />
                ⚠ RESOLVE BREACHED
              </span>
            ) : (
              <span className="text-on-surface font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-primary radar-live" />
                {sla?.minutes_to_resolve_deadline ? `${Math.round(sla.minutes_to_resolve_deadline / 60)}h remaining` : 'Active'}
              </span>
            )}
          </div>
        </div>

        {risk && (
          <div className={`p-3.5 rounded-xl border flex flex-col justify-between card-3d ${
            risk.risk_level === 'Critical' || risk.risk_level === 'High'
              ? 'bg-error/10 border-error/40 text-error shadow-sm'
              : 'liquid-glass border-outline-variant/35 text-on-surface'
          }`}>
            <span className="text-[10px] uppercase font-bold tracking-wider">
              Sweep Risk Assessment
            </span>
            <div className="mt-1.5 font-bold flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${risk.risk_level === 'Critical' || risk.risk_level === 'High' ? 'bg-error radar-breached' : 'bg-primary'}`} />
              [{risk.risk_level}] — Score: {risk.risk_score}
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-1.5 liquid-glass p-1.5 rounded-xl border border-outline-variant/30 text-xs font-mono overflow-x-auto">
        <button
          onClick={() => setActiveTab('messages')}
          className={`px-3.5 py-1.5 rounded-lg transition-all duration-200 press-tactile ${
            activeTab === 'messages'
              ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
          }`}
        >
          Message Thread
        </button>
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-3.5 py-1.5 rounded-lg transition-all duration-200 press-tactile ${
            activeTab === 'summary'
              ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
          }`}
        >
          AI Case Summary
        </button>
        <button
          onClick={() => setActiveTab('triage')}
          className={`px-3.5 py-1.5 rounded-lg transition-all duration-200 press-tactile ${
            activeTab === 'triage'
              ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
          }`}
        >
          AI Triage & Telemetry
        </button>
        <button
          onClick={() => {
            setActiveTab('timeline');
            loadTimeline();
          }}
          className={`px-3.5 py-1.5 rounded-lg transition-all duration-200 press-tactile ${
            activeTab === 'timeline'
              ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
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
        <div className="space-y-3.5 liquid-glass-elevated p-5 rounded-xl border border-outline-variant/35 card-3d">
          <div className="flex items-center gap-2 text-primary font-mono text-xs font-bold uppercase">
            <span className="material-symbols-outlined text-[20px] text-primary">summarize</span>
            4-Part Structured AI Case Summary (SRS §5.5)
          </div>
          {summary ? (
            <div className="space-y-2.5 text-xs font-sans">
              <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                <strong className="block text-primary font-mono text-[10px] uppercase font-bold tracking-wider mb-1">
                  1. What Was Reported
                </strong>
                <p className="text-on-surface leading-relaxed">{summary.what_was_reported}</p>
              </div>
              <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                <strong className="block text-primary font-mono text-[10px] uppercase font-bold tracking-wider mb-1">
                  2. What Happened Since
                </strong>
                <p className="text-on-surface leading-relaxed">{summary.what_happened_since}</p>
              </div>
              <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                <strong className="block text-primary font-mono text-[10px] uppercase font-bold tracking-wider mb-1">
                  3. What is Confirmed
                </strong>
                <p className="text-on-surface leading-relaxed">{summary.what_is_confirmed}</p>
              </div>
              <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                <strong className="block text-secondary font-mono text-[10px] uppercase font-bold tracking-wider mb-1">
                  4. What Remains Unresolved
                </strong>
                <p className="text-on-surface leading-relaxed">{summary.what_remains_unresolved}</p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant italic font-mono">No AI summary generated yet.</p>
          )}
        </div>
      )}

      {activeTab === 'triage' && (
        <div className="space-y-4 liquid-glass-elevated p-5 rounded-xl border border-outline-variant/35 card-3d">
          <div className="flex items-center justify-between border-b border-outline-variant/20 pb-3">
            <div className="flex items-center gap-2 text-primary font-mono text-xs font-bold uppercase">
              <span className="material-symbols-outlined text-[20px]">psychology</span>
              AI Triage & Diagnostic Telemetry [SRS §5.2]
            </div>
            {triage && (
              <span className="font-mono text-xs px-2.5 py-1 rounded-md bg-primary/10 text-primary font-bold border border-primary/20 shadow-xs">
                CONFIDENCE: {triage.confidence_score !== undefined ? `${Math.round(triage.confidence_score * 100)}%` : (triage.confidence_level || 'HIGH')}
              </span>
            )}
          </div>

          {triage ? (
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                  <span className="block font-mono text-[10px] text-on-surface-variant uppercase font-bold tracking-wider">
                    Suggested Category & Team
                  </span>
                  <strong className="text-on-surface text-sm block mt-0.5">
                    {triage.suggested_category || triage.predicted_category || 'General IT'}
                  </strong>
                  <span className="text-[11px] text-primary font-mono font-semibold block mt-0.5">
                    ➔ {triage.suggested_team || 'Service Desk'}
                  </span>
                </div>

                <div className="p-3 liquid-glass rounded-lg border border-outline-variant/30 card-3d">
                  <span className="block font-mono text-[10px] text-on-surface-variant uppercase font-bold tracking-wider">
                    Predicted Severity & Priority
                  </span>
                  <strong className="text-secondary font-mono text-sm block mt-0.5">
                    [{triage.suggested_priority || triage.predicted_priority || 'P3'}]
                  </strong>
                  <span className="text-[11px] text-on-surface-variant font-mono block mt-0.5">
                    Confidence: {triage.confidence_score !== undefined ? `${Math.round(triage.confidence_score * 100)}%` : (triage.confidence_level || 'HIGH')}
                  </span>
                </div>
              </div>

              {/* Supporting Telemetry Factors */}
              {triage.supporting_factors && triage.supporting_factors.length > 0 && (
                <div className="p-3.5 liquid-glass rounded-lg border border-tertiary/20 card-3d">
                  <span className="block font-mono text-[10px] text-tertiary font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[14px]">tune</span>
                    Supporting Telemetry & Factors
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                    {triage.supporting_factors.map((factor, i) => (
                      <li key={i} className="leading-relaxed">{factor}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Missing Info Clarification Questions */}
              {((triage.missing_info_questions && triage.missing_info_questions.length > 0) || (triage.missing_info && triage.missing_info.length > 0)) && (
                <div className="p-3.5 liquid-glass rounded-lg border-l-4 border-l-secondary border border-outline-variant/30 card-3d">
                  <span className="block font-mono text-[10px] text-secondary font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[14px]">help_center</span>
                    Suggested Clarification Questions (Missing Info - SRS §5.4)
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                    {(triage.missing_info_questions || triage.missing_info || []).map((q, i) => (
                      <li key={i} className="leading-relaxed">{q}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Next Action */}
              {triage.recommended_next_action && (
                <div className="p-3 liquid-glass rounded-lg border border-primary/25 text-xs font-mono flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">alt_route</span>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-primary block">Recommended Next Action:</span>
                    <span className="text-on-surface">{triage.recommended_next_action}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant italic font-mono">No AI triage assessment recorded.</p>
          )}
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
          {timeline.length === 0 ? (
            <p className="text-xs text-on-surface-variant italic font-mono p-4 liquid-glass rounded-lg">No audit records recorded.</p>
          ) : (
            timeline.map((item) => (
              <div
                key={item.id}
                className="p-3 liquid-glass-interactive rounded-lg text-xs flex items-center justify-between font-mono card-3d"
              >
                <div>
                  <span className="font-bold text-on-surface block">{item.action}</span>
                  <span className="block text-[10px] text-on-surface-variant">
                    Actor: {item.actor_email || 'System'}
                  </span>
                </div>
                <span className="text-[10px] text-on-surface-variant bg-surface-container/60 px-2 py-0.5 rounded">
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
            ))
          )}
        </div>
      )}

      {/* Candidate Similar Cases (SRS §5.7) */}
      {similarCases.length > 0 && (
        <div className="p-4 liquid-glass rounded-xl border border-outline-variant/30 space-y-2.5 card-3d">
          <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-tertiary">
            <span className="material-symbols-outlined text-[16px]">content_copy</span>
            Candidate Duplicate / Similar Cases (Suggestions Only)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {similarCases.map((sc) => (
              <div key={sc.id} className="p-2.5 liquid-glass-interactive rounded-lg text-xs font-mono flex items-center justify-between">
                <div className="min-w-0 pr-2">
                  <span className="font-bold text-primary">#{sc.reference_number}</span>
                  <span className="block text-[11px] text-on-surface truncate">{sc.title}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 bg-tertiary-container/30 text-tertiary font-bold rounded-md flex-shrink-0">
                  {Math.round(sc.similarity_score * 100)}% match
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Escalation Modal */}
      {escalateOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleEscalate} className="liquid-glass-elevated p-6 rounded-2xl max-w-md w-full space-y-4 border border-outline-variant/40 shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center gap-2 text-error">
              <span className="material-symbols-outlined text-[24px]">warning</span>
              <h3 className="font-headline font-bold text-base text-on-surface">
                Level 2 Human Escalation Request
              </h3>
            </div>
            <p className="text-xs text-on-surface-variant font-sans">
              Explicit operator request for Team Lead / Manager intervention per SRS §6.4.
            </p>
            <textarea
              required
              rows={3}
              value={escalateReason}
              onChange={(e) => setEscalateReason(e.target.value)}
              placeholder="State reason for escalation, vendor roadblock, or SLA emergency..."
              className="w-full p-3 input-liquid rounded-xl text-xs text-on-surface font-sans"
            />
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setEscalateOpen(false)}
                className="px-4 py-2 bg-surface-container hover:bg-surface-container-highest text-xs font-mono font-semibold rounded-lg transition-colors press-tactile"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-2 bg-error hover:bg-error/90 text-on-error text-xs font-mono font-bold rounded-lg transition-all duration-200 press-tactile shadow-sm"
              >
                {actionLoading ? 'Broadcasting...' : 'Broadcast Escalation'}
              </button>
            </div>
          </form>
        </div>
      )}

      {reopenOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleReopen} className="liquid-glass-elevated p-6 rounded-2xl max-w-md w-full space-y-4 border border-outline-variant/40 shadow-2xl animate-in zoom-in-95 duration-200">
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
              className="w-full p-3 input-liquid rounded-xl text-xs text-on-surface font-sans"
            />
            <div className="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setReopenOpen(false)}
                className="px-4 py-2 bg-surface-container hover:bg-surface-container-highest text-xs font-mono font-semibold rounded-lg transition-colors press-tactile"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-2 bg-secondary hover:bg-secondary/90 text-on-secondary text-xs font-mono font-bold rounded-lg transition-all duration-200 press-tactile shadow-sm"
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
