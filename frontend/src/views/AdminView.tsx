import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export const AdminView: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'users' | 'system'>('profile');

  const usersList = [
    { email: 'requester@assistiq.local', role: 'Requester', team: 'Field Operations', status: 'Active' },
    { email: 'operator@assistiq.local', role: 'Operator', team: 'Tier 1 Support', status: 'Active' },
    { email: 'lead@assistiq.local', role: 'TeamLead', team: 'Application Support', status: 'Active' },
    { email: 'manager@assistiq.local', role: 'Manager', team: 'Operations Management', status: 'Active' },
    { email: 'admin@assistiq.local', role: 'Administrator', team: 'System Admin', status: 'Active' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass p-5 rounded-xl border border-outline-variant/40 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary shadow-xs">
            <span className="material-symbols-outlined text-[24px]">admin_panel_settings</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary radar-live" />
              <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
                ADMINISTRATION & PROFILE // RBAC
              </span>
            </div>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              System Administration & User Profile
            </h1>
          </div>
        </div>

        <div className="inline-flex bg-surface-container-lowest/80 backdrop-blur-md p-1 rounded-lg border border-outline-variant/30 text-xs font-mono shadow-xs">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-3 py-1 rounded-md transition-all press-tactile ${
              activeTab === 'profile'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/50'
            }`}
          >
            My Profile
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-3 py-1 rounded-md transition-all press-tactile ${
              activeTab === 'users'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/50'
            }`}
          >
            User Directory
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`px-3 py-1 rounded-md transition-all press-tactile ${
              activeTab === 'system'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/50'
            }`}
          >
            System Status
          </button>
        </div>
      </div>

      {activeTab === 'profile' && user && (
        <div className="liquid-glass-elevated p-6 rounded-xl border border-outline-variant/40 shadow-md space-y-4 max-w-xl animate-fadeIn">
          <div className="flex items-center gap-4 border-b border-outline-variant/20 pb-4">
            <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center text-on-primary text-2xl font-bold font-headline shadow-md">
              {user.email[0].toUpperCase()}
            </div>
            <div>
              <h2 className="font-headline text-xl font-bold text-on-surface">
                {user.email}
              </h2>
              <span className="inline-block font-mono text-xs text-primary font-bold bg-primary-container px-2.5 py-0.5 rounded-full mt-1.5 shadow-xs">
                ROLE: {user.role}
              </span>
            </div>
          </div>

          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex justify-between py-2 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">User ID:</span>
              <span className="text-on-surface font-semibold">{user.id}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">Account Status:</span>
              <span className="text-primary font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-primary radar-live" />
                Active & Verified
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">Auth Provider:</span>
              <span className="text-on-surface">Argon2id + JWT Dual-Path</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="liquid-glass rounded-xl p-5 border border-outline-variant/30 shadow-sm space-y-4 animate-fadeIn">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[20px]">badge</span>
            <h2 className="font-headline text-base font-bold text-on-surface">
              Role-Based Access Control (RBAC) User Directory
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-outline-variant/30 text-on-surface-variant text-[11px]">
                  <th className="py-2.5 px-3 uppercase tracking-wider">Email</th>
                  <th className="py-2.5 px-3 uppercase tracking-wider">Role</th>
                  <th className="py-2.5 px-3 uppercase tracking-wider">Team</th>
                  <th className="py-2.5 px-3 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u) => (
                  <tr key={u.email} className="border-b border-outline-variant/20 hover:bg-surface-container/40 transition-colors">
                    <td className="py-3 px-3 font-bold text-on-surface">{u.email}</td>
                    <td className="py-3 px-3">
                      <span className="px-2.5 py-0.5 rounded-full bg-surface-container-high/80 font-bold text-primary border border-outline-variant/30">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-on-surface-variant">{u.team}</td>
                    <td className="py-3 px-3 text-primary font-bold flex items-center gap-1.5 mt-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                      {u.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fadeIn">
          <div className="p-5 liquid-glass-interactive rounded-xl border border-outline-variant/30 space-y-2.5 font-mono text-xs card-3d">
            <div className="flex items-center justify-between text-on-surface-variant uppercase font-bold text-[10px]">
              <span>Backend Engine</span>
              <span className="material-symbols-outlined text-primary text-[18px]">terminal</span>
            </div>
            <div className="font-bold text-sm text-primary font-headline">FastAPI + Python 3.14</div>
            <p className="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Zero-cost in-process scheduler architecture with APScheduler Sweep.
            </p>
          </div>

          <div className="p-5 liquid-glass-interactive rounded-xl border border-outline-variant/30 space-y-2.5 font-mono text-xs card-3d">
            <div className="flex items-center justify-between text-on-surface-variant uppercase font-bold text-[10px]">
              <span>Database & Storage</span>
              <span className="material-symbols-outlined text-primary text-[18px]">database</span>
            </div>
            <div className="font-bold text-sm text-primary font-headline">PostgreSQL 16 + pg_trgm</div>
            <p className="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Supabase Postgres & Storage with magic bytes MIME validation.
            </p>
          </div>

          <div className="p-5 liquid-glass-interactive rounded-xl border border-outline-variant/30 space-y-2.5 font-mono text-xs card-3d">
            <div className="flex items-center justify-between text-on-surface-variant uppercase font-bold text-[10px]">
              <span>AI Model Provider</span>
              <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
            </div>
            <div className="font-bold text-sm text-primary font-headline">Google Gemini 2.5 Flash</div>
            <p className="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Structured JSON triage analysis, 4-part summaries, and draft assistant.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
