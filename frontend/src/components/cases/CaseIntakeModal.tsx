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
    <div className="fixed inset-0 z-50 overflow-y-auto bg-inverse-surface/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-surface-container-high rounded-lg max-w-2xl w-full p-6 shadow-xl border border-outline-variant/40 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-3">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse" />
            <span className="font-mono text-xs text-primary font-bold tracking-wider uppercase">
              NEW DOCKET INTAKE // AI TRIAGE
            </span>
          </div>
          <button
            onClick={handleReset}
            className="w-8 h-8 rounded hover:bg-surface-container flex items-center justify-center text-on-surface-variant"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {error && (
          <div className="p-3 bg-error-container text-on-error-container text-xs rounded border border-error/20">
            {error}
          </div>
        )}

        {!createdCase ? (
          /* Intake Form */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1">
                Docket Title / Summary
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Substation 4 conveyor line suddenly halted after calibration"
                className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-sm text-on-surface focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1">
                Detailed Statement / Symptoms
              </label>
              <textarea
                required
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe exact symptoms, error codes, affected hardware, and immediate impact..."
                className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-sm text-on-surface focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Type
                </label>
                <select
                  value={caseType}
                  onChange={(e) => setCaseType(e.target.value as CaseType)}
                  className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
                >
                  <option value="Incident">Incident</option>
                  <option value="ServiceRequest">Service Request</option>
                </select>
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
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
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Initial Severity
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as CasePriority)}
                  className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
                >
                  <option value="P1">P1 - Critical (15m resp / 4h sla)</option>
                  <option value="P2">P2 - High (1h resp / 8h sla)</option>
                  <option value="P3">P3 - Medium (4h resp / 72h sla)</option>
                  <option value="P4">P4 - Low (24h resp / 120h sla)</option>
                </select>
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Site / Facility
                </label>
                <input
                  type="text"
                  value={site}
                  onChange={(e) => setSite(e.target.value)}
                  placeholder="e.g. Substation 4"
                  className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-outline-variant/30">
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-surface-container hover:bg-surface-container-highest text-on-surface font-mono text-xs rounded transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors uppercase tracking-wider flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[16px]">psychology</span>
                {loading ? 'Submitting & Triaging...' : 'Submit & Run AI Triage'}
              </button>
            </div>
          </form>
        ) : (
          /* Post-Creation AI Triage Review Card (Matching Stitch Screen 1 & 2) */
          <div className="space-y-4">
            <div className="p-4 bg-surface-container-low rounded border border-outline-variant/40">
              <div className="flex items-center justify-between mb-2">
                <span className="font-headline font-bold text-base text-on-surface">
                  {createdCase.reference_number}: {createdCase.title}
                </span>
                <span className="font-mono text-xs bg-primary text-on-primary px-2 py-0.5 rounded font-bold">
                  {createdCase.status}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant italic font-sans">
                "{createdCase.description}"
              </p>
            </div>

            {triageLoading ? (
              <div className="p-8 text-center bg-surface-container-lowest rounded border border-outline-variant/30 flex flex-col items-center gap-2">
                <span className="material-symbols-outlined text-primary text-3xl animate-spin">
                  sync
                </span>
                <span className="font-mono text-xs text-primary font-semibold">
                  Analyzing Case Symptoms with Gemini AI Model...
                </span>
              </div>
            ) : triageResult ? (
              <div className="space-y-3">
                {/* AI Confidence & Predictions */}
                <div className="bg-surface-container-lowest p-4 rounded border border-outline-variant/30 space-y-3">
                  <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2">
                    <div className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-primary text-[18px]">
                        psychology
                      </span>
                      <span className="font-mono text-xs text-primary font-bold uppercase">
                        AI Triage Assessment [SRS §5.2]
                      </span>
                    </div>
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-primary-container text-on-primary-container font-semibold">
                      CONFIDENCE: {triageResult.confidence_score !== undefined ? `${Math.round(triageResult.confidence_score * 100)}%` : (triageResult.confidence_level || 'HIGH')}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-2.5 bg-surface-container-low rounded">
                      <span className="block font-mono text-[10px] text-on-surface-variant uppercase">
                        Recommended Category
                      </span>
                      <strong className="text-on-surface text-sm">
                        {triageResult.suggested_category || triageResult.predicted_category || 'General IT'}
                      </strong>
                    </div>

                    <div className="p-2.5 bg-surface-container-low rounded">
                      <span className="block font-mono text-[10px] text-on-surface-variant uppercase">
                        Predicted Severity
                      </span>
                      <strong className="text-secondary font-mono text-sm">
                        [{triageResult.suggested_priority || triageResult.predicted_priority || 'P3'}]
                      </strong>
                    </div>
                  </div>

                  {/* Supporting Factors */}
                  {triageResult.supporting_factors && triageResult.supporting_factors.length > 0 && (
                    <div className="p-3 bg-surface-container-low rounded">
                      <span className="block font-mono text-[10px] text-tertiary font-bold uppercase mb-1">
                        Supporting Telemetry & Factors
                      </span>
                      <ul className="list-disc list-inside space-y-0.5 text-xs text-on-surface">
                        {triageResult.supporting_factors.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Missing Info Questions (SRS §5.4) */}
                  {((triageResult.missing_info_questions && triageResult.missing_info_questions.length > 0) || (triageResult.missing_info && triageResult.missing_info.length > 0)) && (
                    <div className="p-3 bg-surface-container-high rounded border-l-2 border-secondary">
                      <span className="block font-mono text-[10px] text-secondary font-bold uppercase mb-1">
                        Suggested Clarification Questions (Missing Info)
                      </span>
                      <ul className="list-disc list-inside space-y-0.5 text-xs text-on-surface">
                        {(triageResult.missing_info_questions || triageResult.missing_info || []).map((q, i) => (
                          <li key={i}>{q}</li>
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
                className="px-4 py-2 bg-primary text-on-primary font-mono text-xs font-bold rounded shadow-xs"
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
