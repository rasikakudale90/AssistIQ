import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Case, CasePriority } from '../api/types';
import { listCasesApi } from '../api/cases';
import { CaseDetail } from '../components/cases/CaseDetail';
import { CaseIntakeModal } from '../components/cases/CaseIntakeModal';

export const WorkbenchView: React.FC = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterTab, setFilterTab] = useState<'ALL' | 'ACTIVE' | 'BREACHED' | 'UNASSIGNED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [intakeModalOpen, setIntakeModalOpen] = useState(false);

  const isStaff = user && user.role !== 'Requester';

  const fetchCases = async () => {
    setLoading(true);
    try {
      const data = await listCasesApi();
      const safeData = Array.isArray(data) ? data : [];
      setCases(safeData);
      if (safeData.length > 0 && !selectedCase) {
        setSelectedCase(safeData[0]);
      } else if (selectedCase) {
        const found = safeData.find((c) => c.id === selectedCase.id);
        if (found) setSelectedCase(found);
      }
    } catch {
      setCases([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [user]);

  const safeList = Array.isArray(cases) ? cases : [];

  const filteredCases = safeList.filter((c) => {
    const title = c.title || '';
    const ref = c.reference_number || '';
    const cat = c.category || c.service_id || '';
    const query = searchQuery.toLowerCase();

    const matchesSearch =
      title.toLowerCase().includes(query) ||
      ref.toLowerCase().includes(query) ||
      cat.toLowerCase().includes(query);

    if (!matchesSearch) return false;

    if (filterTab === 'ACTIVE') {
      return !['Resolved', 'Closed', 'Cancelled'].includes(c.status);
    }
    if (filterTab === 'BREACHED') {
      return c.sla?.response_breached || c.sla?.resolve_breached;
    }
    if (filterTab === 'UNASSIGNED') {
      return !c.assigned_operator_id && !c.owner_id && !['Resolved', 'Closed', 'Cancelled'].includes(c.status);
    }
    return true;
  });

  const priorityColors: Record<CasePriority, string> = {
    P1: 'bg-error text-on-error',
    P2: 'bg-secondary text-on-secondary',
    P3: 'bg-tertiary-container text-on-tertiary-container',
    P4: 'bg-surface-container-high text-on-surface-variant',
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Workbench Header & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass p-5 rounded-xl border border-outline-variant/35 shadow-sm card-3d">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xs">
            <span className="material-symbols-outlined text-[24px]">handyman</span>
          </div>
          <div>
            <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider block">
              MW-OS // IT BENCH
            </span>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              {isStaff ? 'Field Operations & Workshop IT Console' : 'My Support Requests'}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIntakeModalOpen(true)}
            className="px-4 py-2.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-sm transition-all duration-200 flex items-center gap-2 uppercase press-tactile"
          >
            <span className="material-symbols-outlined text-[18px]">add_circle</span>
            <span>New Docket Intake</span>
          </button>
        </div>
      </div>

      {/* Split-View Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Ticket Queue & Filters */}
        <div className="lg:col-span-5 space-y-3">
          {/* Filter Pills & Search */}
          <div className="space-y-2.5">
            <div className="flex items-center gap-1.5 liquid-glass p-1.5 rounded-lg border border-outline-variant/30 overflow-x-auto text-xs font-mono">
              <button
                onClick={() => setFilterTab('ALL')}
                className={`px-3 py-1.5 rounded-md transition-all duration-200 press-tactile ${
                  filterTab === 'ALL'
                    ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
                }`}
              >
                ALL ({safeList.length})
              </button>
              <button
                onClick={() => setFilterTab('ACTIVE')}
                className={`px-3 py-1.5 rounded-md transition-all duration-200 press-tactile ${
                  filterTab === 'ACTIVE'
                    ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
                }`}
              >
                ACTIVE
              </button>
              <button
                onClick={() => setFilterTab('BREACHED')}
                className={`px-3 py-1.5 rounded-md transition-all duration-200 press-tactile ${
                  filterTab === 'BREACHED'
                    ? 'bg-secondary text-on-secondary font-bold shadow-xs scale-[1.02]'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
                }`}
              >
                BREACHED
              </button>
              <button
                onClick={() => setFilterTab('UNASSIGNED')}
                className={`px-3 py-1.5 rounded-md transition-all duration-200 press-tactile ${
                  filterTab === 'UNASSIGNED'
                    ? 'bg-primary text-on-primary font-bold shadow-xs scale-[1.02]'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
                }`}
              >
                UNASSIGNED
              </button>
            </div>

            <div className="relative flex items-center">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-primary dark:text-primary-fixed text-[20px] pointer-events-none z-10 transition-colors">
                search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter by ref, keyword, category..."
                className="w-full pl-10 pr-3.5 py-2.5 input-liquid rounded-xl text-xs text-on-surface placeholder:text-on-surface-variant/70 font-mono shadow-xs focus:outline-none"
              />
            </div>
          </div>

          {/* Ticket Cards List */}
          <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1">
            {loading ? (
              <div className="space-y-2.5 p-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="p-4 rounded-lg shimmer-warm h-24 border border-outline-variant/20" />
                ))}
              </div>
            ) : filteredCases.length === 0 ? (
              <div className="p-8 text-center liquid-glass rounded-lg border border-outline-variant/30 font-mono text-xs text-on-surface-variant italic">
                No tickets matching current filter.
              </div>
            ) : (
              filteredCases.map((c) => {
                const isSelected = selectedCase?.id === c.id;
                const isBreached = c.sla?.response_breached || c.sla?.resolve_breached;
                return (
                  <div
                    key={c.id}
                    onClick={() => setSelectedCase(c)}
                    className={`p-3.5 rounded-xl border transition-all duration-200 cursor-pointer space-y-2.5 card-3d press-tactile ${
                      isSelected
                        ? 'liquid-glass border-primary shadow-md ring-2 ring-primary/30 scale-[1.01]'
                        : 'liquid-glass-interactive'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-primary">#{c.reference_number || c.id.slice(0, 8)}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold shadow-xs ${priorityColors[c.priority] || 'bg-surface-container'}`}>
                          {c.priority}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {isBreached && (
                          <span className="px-2 py-0.5 bg-error text-on-error rounded text-[9px] font-bold radar-breached">
                            BREACH
                          </span>
                        )}
                        <span className="px-2 py-0.5 bg-surface-container-high/80 rounded text-[10px] text-on-surface font-semibold uppercase">
                          {c.status}
                        </span>
                      </div>
                    </div>

                    <h3 className="font-headline font-semibold text-sm text-on-surface line-clamp-1">
                      {c.title}
                    </h3>

                    <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant pt-2 border-t border-outline-variant/20">
                      <span>📁 {c.category || c.service_id || 'General Support'}</span>
                      <span>{c.created_at ? new Date(c.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : 'Today'}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Case Detail Pane */}
        <div className="lg:col-span-7">
          {selectedCase ? (
            <CaseDetail
              caseItem={selectedCase}
              onCaseUpdated={(updated) => {
                setSelectedCase(updated);
                fetchCases();
              }}
            />
          ) : (
            <div className="p-12 text-center liquid-glass rounded-xl border border-outline-variant/30 font-mono text-xs text-on-surface-variant">
              Select a case from the workbench queue to inspect details.
            </div>
          )}
        </div>
      </div>

      {/* Case Intake Modal */}
      <CaseIntakeModal
        isOpen={intakeModalOpen}
        onClose={() => setIntakeModalOpen(false)}
        onCaseCreated={(newCase) => {
          fetchCases();
          setSelectedCase(newCase);
        }}
      />
    </div>
  );
};
