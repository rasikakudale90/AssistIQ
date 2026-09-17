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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-high p-4 rounded border border-outline-variant/30 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[24px]">admin_panel_settings</span>
          <div>
            <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
              ADMINISTRATION & PROFILE // RBAC
            </span>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              System Administration & User Profile
            </h1>
          </div>
        </div>

        <div className="inline-flex bg-surface-container-lowest p-1 rounded border border-outline-variant/30 text-xs font-mono">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-3 py-1 rounded transition-colors ${
              activeTab === 'profile'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            My Profile
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-3 py-1 rounded transition-colors ${
              activeTab === 'users'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            User Directory
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`px-3 py-1 rounded transition-colors ${
              activeTab === 'system'
                ? 'bg-primary text-on-primary font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            System Status
          </button>
        </div>
      </div>

      {activeTab === 'profile' && user && (
        <div className="bg-surface-container-lowest p-6 rounded-lg border border-outline-variant/30 shadow-xs space-y-4 max-w-xl">
          <div className="flex items-center gap-4 border-b border-outline-variant/20 pb-4">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-on-primary text-2xl font-bold font-headline">
              {user.email[0].toUpperCase()}
            </div>
            <div>
              <h2 className="font-headline text-xl font-bold text-on-surface">
                {user.email}
              </h2>
              <span className="inline-block font-mono text-xs text-primary font-bold bg-primary-fixed px-2 py-0.5 rounded mt-1">
                ROLE: {user.role}
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1.5 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">User ID:</span>
              <span className="text-on-surface font-semibold">{user.id}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">Account Status:</span>
              <span className="text-primary font-semibold">Active & Verified</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-outline-variant/10">
              <span className="text-on-surface-variant">Auth Provider:</span>
              <span className="text-on-surface">Argon2id + JWT Dual-Path</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="bg-surface-container-lowest p-5 rounded-lg border border-outline-variant/30 shadow-xs space-y-4">
          <h2 className="font-headline text-base font-bold text-on-surface">
            Role-Based Access Control (RBAC) User Directory
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-outline-variant/30 text-on-surface-variant">
                  <th className="py-2 px-3">Email</th>
                  <th className="py-2 px-3">Role</th>
                  <th className="py-2 px-3">Team</th>
                  <th className="py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u) => (
                  <tr key={u.email} className="border-b border-outline-variant/20 hover:bg-surface-container-high/40">
                    <td className="py-2.5 px-3 font-bold text-on-surface">{u.email}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-surface-container font-bold text-primary">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-on-surface-variant">{u.team}</td>
                    <td className="py-2.5 px-3 text-primary font-bold">● {u.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-surface-container-low rounded border border-outline-variant/30 space-y-2 font-mono text-xs">
            <span className="text-on-surface-variant uppercase font-bold text-[10px]">Backend Engine</span>
            <div className="font-bold text-sm text-primary">FastAPI + Python 3.14</div>
            <p className="text-[11px] text-on-surface-variant font-sans">
              Zero-cost in-process scheduler architecture with APScheduler Sweep.
            </p>
          </div>

          <div className="p-4 bg-surface-container-low rounded border border-outline-variant/30 space-y-2 font-mono text-xs">
            <span className="text-on-surface-variant uppercase font-bold text-[10px]">Database & Storage</span>
            <div className="font-bold text-sm text-primary">PostgreSQL 16 + pg_trgm</div>
            <p className="text-[11px] text-on-surface-variant font-sans">
              Supabase Postgres & Storage with magic bytes MIME validation.
            </p>
          </div>

          <div className="p-4 bg-surface-container-low rounded border border-outline-variant/30 space-y-2 font-mono text-xs">
            <span className="text-on-surface-variant uppercase font-bold text-[10px]">AI Model Provider</span>
            <div className="font-bold text-sm text-primary">Google Gemini 2.5 Flash</div>
            <p className="text-[11px] text-on-surface-variant font-sans">
              Structured JSON triage analysis, 4-part summaries, and draft assistant.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
