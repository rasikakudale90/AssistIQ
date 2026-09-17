import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../api/types';

export const LoginView: React.FC = () => {
  const { login, switchDemoRole, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid email or password');
    }
  };

  const demoRoles: Array<{ role: UserRole; title: string; email: string; desc: string }> = [
    {
      role: 'Requester',
      title: 'Field Requester',
      email: 'requester@assistiq.local',
      desc: 'Submit incidents, track status, view public notes',
    },
    {
      role: 'Operator',
      title: 'Tier 1 Operator',
      email: 'operator@assistiq.local',
      desc: 'Triage workbench, internal notes, AI draft assistance',
    },
    {
      role: 'TeamLead',
      title: 'Support Team Lead',
      email: 'lead@assistiq.local',
      desc: 'Queue routing, SLA monitoring, escalations',
    },
    {
      role: 'Manager',
      title: 'IT Helpdesk Manager',
      email: 'manager@assistiq.local',
      desc: 'Operational insights, AI narrative, CSV reports',
    },
    {
      role: 'Administrator',
      title: 'System Administrator',
      email: 'admin@assistiq.local',
      desc: 'Full RBAC, team administration, audit trails',
    },
  ];

  return (
    <div className="min-h-screen bg-surface flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-12 h-12 rounded bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-2xl mx-auto shadow-md">
          AI
        </div>
        <h2 className="mt-3 font-headline text-2xl font-bold text-on-surface">
          AssistIQ IT Helpdesk
        </h2>
        <p className="mt-1 font-mono text-xs text-primary font-medium tracking-wider uppercase">
          MW-OS // BENCH AUTHENTICATION
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-surface-container-high py-8 px-6 shadow-sm rounded-lg border border-outline-variant/30">
          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-error-container text-on-error-container text-xs rounded border border-error/20">
                {error}
              </div>
            )}

            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.local"
                className="mt-1 block w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 rounded text-sm text-on-surface focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 block w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 rounded text-sm text-on-surface focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2 px-4 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors uppercase tracking-wider"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          {/* Quick 1-Click Demo Personas */}
          <div className="mt-6 pt-6 border-t border-outline-variant/30">
            <div className="flex items-center gap-1.5 mb-3">
              <span className="material-symbols-outlined text-primary text-[16px]">key</span>
              <span className="font-mono text-[11px] text-primary uppercase font-bold tracking-wider">
                Instant 1-Click Demo Personas
              </span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {demoRoles.map((d) => (
                <button
                  key={d.role}
                  type="button"
                  onClick={() => switchDemoRole(d.role)}
                  className="flex items-center justify-between p-2.5 bg-surface-container-lowest hover:bg-surface-container rounded border border-outline-variant/30 text-left transition-colors group"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono text-xs font-bold text-on-surface">
                        {d.title}
                      </span>
                      <span className="font-mono text-[10px] text-primary font-semibold">
                        [{d.role}]
                      </span>
                    </div>
                    <span className="block font-sans text-[11px] text-on-surface-variant truncate">
                      {d.desc}
                    </span>
                  </div>
                  <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:text-primary transition-colors flex-shrink-0">
                    arrow_forward
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
