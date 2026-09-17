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
      setCases(data);
      if (data.length > 0 && !selectedCase) {
        setSelectedCase(data[0]);
      } else if (selectedCase) {
        const found = data.find((c) => c.id === selectedCase.id);
        if (found) setSelectedCase(found);
      }
    } catch {
      // Ignored
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [user]);

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.reference_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.category.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (filterTab === 'ACTIVE') {
      return !['Resolved', 'Closed', 'Cancelled'].includes(c.status);
    }
    if (filterTab === 'BREACHED') {
      return c.sla?.response_breached || c.sla?.resolve_breached;
    }
    if (filterTab === 'UNASSIGNED') {
      return !c.assigned_operator_id && !['Resolved', 'Closed', 'Cancelled'].includes(c.status);
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-high p-4 rounded border border-outline-variant/30 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[22px]">handyman</span>
          <div>
            <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
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
            className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors flex items-center gap-1.5 uppercase"
          >
            <span className="material-symbols-outlined text-[16px]">add_circle</span>
            <span>New Docket Intake</span>
          </button>
        </div>
      </div>

      {/* Split-View Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Ticket Queue & Filters */}
        <div className="lg:col-span-5 space-y-3">
          {/* Filter Pills & Search */}
          <div className="space-y-2">
            <div className="flex items-center gap-1 bg-surface-container-lowest p-1 rounded border border-outline-variant/30 overflow-x-auto text-xs font-mono">
              <button
                onClick={() => setFilterTab('ALL')}
                className={`px-2.5 py-1 rounded transition-colors ${
                  filterTab === 'ALL'
                    ? 'bg-primary text-on-primary font-bold shadow-xs'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                ALL ({cases.length})
              </button>
              <button
                onClick={() => setFilterTab('ACTIVE')}
                className={`px-2.5 py-1 rounded transition-colors ${
                  filterTab === 'ACTIVE'
                    ? 'bg-primary text-on-primary font-bold shadow-xs'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                ACTIVE
              </button>
              <button
                onClick={() => setFilterTab('BREACHED')}
                className={`px-2.5 py-1 rounded transition-colors ${
                  filterTab === 'BREACHED'
                    ? 'bg-secondary text-on-secondary font-bold shadow-xs'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                BREACHED
              </button>
              <button
                onClick={() => setFilterTab('UNASSIGNED')}
                className={`px-2.5 py-1 rounded transition-colors ${
                  filterTab === 'UNASSIGNED'
                    ? 'bg-primary text-on-primary font-bold shadow-xs'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                UNASSIGNED
              </button>
            </div>

            <div className="relative">
              <span className="material-symbols-outlined absolute left-2.5 top-2.5 text-on-surface-variant text-[16px]">
                search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter by ref, keyword, category..."
                className="w-full pl-8 pr-3 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface placeholder:text-on-surface-variant/70 focus:outline-none focus:ring-1 focus:ring-primary font-mono"
              />
            </div>
          </div>

          {/* Ticket Cards List */}
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {loading ? (
              <div className="p-8 text-center font-mono text-xs text-on-surface-variant">
                Loading workbench tickets...
              </div>
            ) : filteredCases.length === 0 ? (
              <div className="p-8 text-center bg-surface-container-low rounded border border-outline-variant/30 font-mono text-xs text-on-surface-variant italic">
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
                    className={`p-3.5 rounded border transition-all cursor-pointer space-y-2 ${
                      isSelected
                        ? 'bg-surface-container-lowest border-primary shadow-sm ring-1 ring-primary/40'
                        : 'bg-surface-container-lowest border-outline-variant/30 hover:border-outline-variant hover:bg-surface-container-low'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-primary">#{c.reference_number}</span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${priorityColors[c.priority]}`}>
                          {c.priority}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        {isBreached && (
                          <span className="px-1.5 py-0.2 bg-error text-on-error rounded text-[9px] font-bold">
                            BREACH
                          </span>
                        )}
                        <span className="px-1.5 py-0.2 bg-surface-container-high rounded text-[10px] text-on-surface font-semibold uppercase">
                          {c.status}
                        </span>
                      </div>
                    </div>

                    <h3 className="font-headline font-semibold text-sm text-on-surface line-clamp-1">
                      {c.title}
                    </h3>

                    <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant pt-1 border-t border-outline-variant/20">
                      <span>📁 {c.category}</span>
                      <span>{new Date(c.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
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
            <div className="p-12 text-center bg-surface-container-high rounded-lg border border-outline-variant/30 font-mono text-xs text-on-surface-variant">
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
