import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { DashboardStats } from '../../api/types';
import { getDashboardStatsApi } from '../../api/insights';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    if (user && user.role !== 'Requester') {
      getDashboardStatsApi()
        .then(setStats)
        .catch(() => {});
    }
  }, [user]);

  return (
    <header className="fixed top-0 w-full z-50 bg-surface-container-low/95 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-outline-variant/30">
      <div className="h-16 px-4 md:px-6 flex items-center justify-between gap-4 max-w-7xl mx-auto">
        {/* Brand & Identity */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-lg shadow-sm">
            AI
          </div>
          <div className="flex flex-col min-w-0">
            <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
              MW-OS // HELPDESK
            </span>
            <span className="font-headline text-base font-bold text-on-surface truncate">
              AssistIQ Console
            </span>
          </div>
        </div>

        {/* Live Active Stats Pill (Staff Only) */}
        {stats && user?.role !== 'Requester' && (
          <div className="hidden md:flex items-center gap-2 bg-surface-container-lowest px-3 py-1 rounded border border-outline-variant/40 shadow-xs text-xs font-mono">
            <span className="flex items-center gap-1.5 text-on-surface">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              Active: <strong>{stats.active_cases}</strong>
            </span>
            <span className="text-outline-variant">|</span>
            <span className="text-secondary flex items-center gap-1">
              Breached: <strong>{stats.breached_cases}</strong>
            </span>
            <span className="text-outline-variant">|</span>
            <span className="text-tertiary flex items-center gap-1">
              Unassigned: <strong>{stats.unassigned_cases}</strong>
            </span>
          </div>
        )}

        {/* User Profile & Account Actions */}
        <div className="flex items-center gap-3 flex-shrink-0">
          {user && (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2.5 bg-surface-container-high hover:bg-surface-container-highest px-3 py-1.5 rounded transition-colors border border-outline-variant/40"
              >
                <div className="flex flex-col items-end text-right">
                  <span className="font-mono text-[11px] text-on-surface font-semibold truncate max-w-[140px]">
                    {user.email}
                  </span>
                  <span className="font-mono text-[9px] uppercase tracking-wider text-primary font-bold">
                    [{user.role}]
                  </span>
                </div>
                <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-on-primary text-xs font-bold shadow-xs">
                  {user.role[0]}
                </div>
                <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                  expand_more
                </span>
              </button>

              {/* User Account Menu Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-surface-container-lowest border border-outline-variant/50 rounded shadow-lg py-2 z-50">
                  <div className="px-3.5 py-2 border-b border-outline-variant/20 mb-1">
                    <span className="block font-mono text-[10px] text-on-surface-variant uppercase tracking-wider">
                      Signed In As
                    </span>
                    <strong className="block text-xs font-mono text-on-surface truncate">
                      {user.email}
                    </strong>
                    <div className="flex items-center gap-2 mt-1 font-mono text-[10px]">
                      <span className="px-1.5 py-0.2 bg-primary/10 text-primary font-bold rounded">
                        {user.role}
                      </span>
                      {user.site && (
                        <span className="text-on-surface-variant truncate">
                          📍 {user.site}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="pt-1">
                    <button
                      onClick={() => {
                        logout();
                        setShowUserMenu(false);
                      }}
                      className="w-full text-left px-3.5 py-2 text-xs text-error hover:bg-error-container/30 flex items-center gap-2 font-mono font-semibold transition-colors"
                    >
                      <span className="material-symbols-outlined text-[16px]">logout</span>
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
