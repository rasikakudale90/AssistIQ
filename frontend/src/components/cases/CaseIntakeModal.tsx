import React, { useState } from 'react';
import { createCaseApi } from '../../api/cases';
import { getCaseTriageApi } from '../../api/ai';
import { Case, CasePriority, CaseType, AITriageResult } from '../../api/types';

interface CaseIntakeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCaseCreated: (newCase: Case) => void;
}

export const CaseIntakeModal: React.FC<CaseIntakeModalProps> = ({ isOpen, onClose, onCaseCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [caseType, setCaseType] = useState<CaseType>('Incident');
  const [category, setCategory] = useState('Hardware');
  const [priority, setPriority] = useState<CasePriority>('P3');
  const [site, setSite] = useState('Main Facility');
  
  const [loading, setLoading] = useState(false);
  const [triageLoading, setTriageLoading] = useState(false);
  const [triageResult, setTriageResult] = useState<AITriageResult | null>(null);
  const [createdCase, setCreatedCase] = useState<Case | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newCase = await createCaseApi({
        title,
        description,
        case_type: caseType,
        category,
        priority,
        site,
      });
      setCreatedCase(newCase);
      onCaseCreated(newCase);

      // Automatically fetch AI triage analysis
      setTriageLoading(true);
      try {
        const triage = await getCaseTriageApi(newCase.id);
        setTriageResult(triage);
      } catch {
        // Triage error fallback
      } finally {
        setTriageLoading(false);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create case');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTitle('');
    setDescription('');
    setCreatedCase(null);
    setTriageResult(null);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-inverse-surface/40 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
      <div className="liquid-glass-elevated rounded-xl max-w-2xl w-full p-6 shadow-2xl border border-outline-variant/50 space-y-5 animate-scaleUp">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-3">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-secondary radar-live" />
            <span className="font-mono text-xs text-primary font-bold tracking-wider uppercase">
              NEW DOCKET INTAKE // AI TRIAGE ENGINE
            </span>
          </div>
          <button
            onClick={handleReset}
            className="w-8 h-8 rounded-lg hover:bg-surface-container/60 flex items-center justify-center text-on-surface-variant press-tactile transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {error && (
          <div className="p-3.5 bg-error-container/80 backdrop-blur-xs text-on-error-container text-xs rounded-lg border border-error/30 shadow-xs animate-shake">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px]">error</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {!createdCase ? (
          /* Intake Form */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                Docket Title / Summary
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Substation 4 conveyor line suddenly halted after calibration"
                className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-lg text-sm text-on-surface input-liquid focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                Description
              </label>
              <textarea
                required
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the issue, symptoms, affected equipment, or service request details..."
                className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-lg text-sm text-on-surface input-liquid focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Type
                </label>
                <select
                  value={caseType}
                  onChange={(e) => setCaseType(e.target.value as CaseType)}
                  className="w-full px-2.5 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded-lg text-xs text-on-surface input-liquid focus:outline-none"
                >
                  <option value="Incident">Incident</option>
                  <option value="ServiceRequest">Service Request</option>
                </select>
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-2.5 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded-lg text-xs text-on-surface input-liquid focus:outline-none"
                >
                  <option value="Hardware">Hardware</option>
                  <option value="Network">Network</option>
                  <option value="Software">Software</option>
                  <option value="Security">Security</option>
                  <option value="Access Control">Access Control</option>
                  <option value="Industrial Control">Industrial Control</option>
                </select>
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Initial Severity
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as CasePriority)}
                  className="w-full px-2.5 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded-lg text-xs text-on-surface font-mono input-liquid focus:outline-none"
                >
                  <option value="P1">P1 - Critical (15m resp / 4h sla)</option>
                  <option value="P2">P2 - High (1h resp / 8h sla)</option>
                  <option value="P3">P3 - Medium (4h resp / 72h sla)</option>
                  <option value="P4">P4 - Low (24h resp / 120h sla)</option>
                </select>
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Site / Facility
                </label>
                <input
                  type="text"
                  value={site}
                  onChange={(e) => setSite(e.target.value)}
                  placeholder="e.g. Substation 4"
                  className="w-full px-2.5 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded-lg text-xs text-on-surface input-liquid focus:outline-none"
                />
              </div>
            </div>

            {/* Severity Guidance Card */}
            {(() => {
              const guide = {
                P1: {
                  label: 'P1 — Critical Severity',
                  sla: '15m First Response • 4h 24/7 Resolution SLA',
                  desc: 'Immediate critical operational stoppage or severe hazard. Core production equipment completely offline.',
                  badgeClass: 'bg-error text-on-error',
                  borderClass: 'border-error/40 bg-error-container/15 text-on-surface',
                },
                P2: {
                  label: 'P2 — High Severity',
                  sla: '1h First Response • 8h 24/7 Resolution SLA',
                  desc: 'Major system impairment with severe performance loss and limited or complex workarounds.',
                  badgeClass: 'bg-secondary text-on-secondary',
                  borderClass: 'border-secondary/40 bg-secondary-container/15 text-on-surface',
                },
                P3: {
                  label: 'P3 — Medium Severity (Default)',
                  sla: '4h First Response • 72h 24/7 Resolution SLA',
                  desc: 'Standard operational issue or routine malfunction where functional workarounds exist.',
                  badgeClass: 'bg-primary text-on-primary',
                  borderClass: 'border-primary/40 bg-primary-container/15 text-on-surface',
                },
                P4: {
                  label: 'P4 — Low Severity',
                  sla: '24h First Response • 120h 24/7 Resolution SLA',
                  desc: 'Minor cosmetic issue, general procedural inquiry, or non-blocking standard service request.',
                  badgeClass: 'bg-tertiary text-on-tertiary',
                  borderClass: 'border-tertiary/40 bg-tertiary-container/15 text-on-surface',
                },
              }[priority];

              return (
                <div className={`p-3 rounded-lg border text-xs flex items-start gap-2.5 transition-all ${guide.borderClass}`}>
                  <span className="material-symbols-outlined text-[18px] text-primary shrink-0 mt-0.5">info</span>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${guide.badgeClass}`}>
                        {priority}
                      </span>
                      <span className="font-headline font-bold text-xs">{guide.label}</span>
                      <span className="text-[11px] font-mono text-primary font-semibold">({guide.sla})</span>
                    </div>
                    <p className="text-[11px] text-on-surface-variant leading-relaxed">
                      {guide.desc}
                    </p>
                  </div>
                </div>
              );
            })()}

            <div className="flex justify-end gap-2.5 pt-4 border-t border-outline-variant/30">
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-surface-container/60 hover:bg-surface-container text-on-surface font-mono text-xs rounded-lg press-tactile transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-md press-tactile transition-all uppercase tracking-wider flex items-center gap-1.5 disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[16px]">psychology</span>
                {loading ? 'Submitting & Triaging...' : 'Submit & Run AI Triage'}
              </button>
            </div>
          </form>
        ) : (
          /* Post-Creation AI Triage Review Card (Matching Stitch Screen 1 & 2) */
          <div className="space-y-4">
            <div className="p-4 liquid-glass rounded-xl border border-outline-variant/40 shadow-xs">
              <div className="flex items-center justify-between mb-2">
                <span className="font-headline font-bold text-base text-on-surface flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-secondary radar-live" />
                  {createdCase.reference_number}: {createdCase.title}
                </span>
                <span className="font-mono text-xs bg-primary text-on-primary px-2.5 py-0.5 rounded-full font-bold shadow-xs">
                  {createdCase.status}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant italic font-sans pl-4 border-l-2 border-primary/30">
                "{createdCase.description}"
              </p>
            </div>

            {triageLoading ? (
              <div className="p-8 text-center liquid-glass rounded-xl border border-outline-variant/30 flex flex-col items-center gap-3">
                <div className="relative flex items-center justify-center w-14 h-14">
                  <div className="absolute inset-0 rounded-full border-2 border-primary/40 animate-ping" />
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary text-2xl animate-spin">
                      sync
                    </span>
                  </div>
                </div>
                <div>
                  <span className="font-mono text-xs text-primary font-bold block">
                    Analyzing Case Symptoms with Gemini AI Model...
                  </span>
                  <span className="text-[11px] text-on-surface-variant font-sans">
                    Extracting supporting telemetry, confidence metrics, and potential missing data
                  </span>
                </div>
              </div>
            ) : triageResult ? (
              <div className="space-y-3">
                {/* AI Confidence & Predictions */}
                <div className="liquid-glass p-4 rounded-xl border border-outline-variant/40 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary text-[20px]">
                        psychology
                      </span>
                      <span className="font-mono text-xs text-primary font-bold uppercase tracking-wider">
                        AI Triage Assessment [SRS §5.2]
                      </span>
                    </div>
                    <span className="font-mono text-xs px-2.5 py-1 rounded-full bg-primary-container text-on-primary-container font-bold shadow-xs flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                      CONFIDENCE: {triageResult.confidence_score !== undefined ? `${Math.round(triageResult.confidence_score * 100)}%` : (triageResult.confidence_level || 'HIGH')}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-surface-container-low/70 rounded-lg border border-outline-variant/30 card-3d">
                      <span className="block font-mono text-[10px] text-on-surface-variant uppercase tracking-wider mb-1">
                        Recommended Category
                      </span>
                      <strong className="text-on-surface text-sm font-headline">
                        {triageResult.suggested_category || triageResult.predicted_category || 'General IT'}
                      </strong>
                    </div>

                    <div className="p-3 bg-surface-container-low/70 rounded-lg border border-outline-variant/30 card-3d">
                      <span className="block font-mono text-[10px] text-on-surface-variant uppercase tracking-wider mb-1">
                        Predicted Severity
                      </span>
                      <strong className="text-secondary font-mono text-sm">
                        [{triageResult.suggested_priority || triageResult.predicted_priority || 'P3'}]
                      </strong>
                    </div>
                  </div>

                  {/* Supporting Factors */}
                  {triageResult.supporting_factors && triageResult.supporting_factors.length > 0 && (
                    <div className="p-3.5 bg-surface-container-low/70 rounded-lg border border-outline-variant/30">
                      <span className="block font-mono text-[10px] text-tertiary font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[14px]">tune</span>
                        Supporting Telemetry & Factors
                      </span>
                      <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                        {triageResult.supporting_factors.map((f, i) => (
                          <li key={i} className="leading-relaxed">{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Missing Info Questions (SRS §5.4) */}
                  {((triageResult.missing_info_questions && triageResult.missing_info_questions.length > 0) || (triageResult.missing_info && triageResult.missing_info.length > 0)) && (
                    <div className="p-3.5 bg-secondary-container/30 backdrop-blur-xs rounded-lg border border-secondary/30">
                      <span className="block font-mono text-[10px] text-secondary font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[14px]">help_outline</span>
                        Suggested Clarification Questions (Missing Info)
                      </span>
                      <ul className="list-disc list-inside space-y-1 text-xs text-on-surface">
                        {(triageResult.missing_info_questions || triageResult.missing_info || []).map((q, i) => (
                          <li key={i} className="leading-relaxed">{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ) : null}

            <div className="flex justify-end pt-3">
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-md press-tactile transition-all"
              >
                Go to Workbench
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
