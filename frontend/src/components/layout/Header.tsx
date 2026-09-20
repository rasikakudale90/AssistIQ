import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { DashboardStats } from '../../api/types';
import { getDashboardStatsApi } from '../../api/insights';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (user && user.role !== 'Requester') {
      getDashboardStatsApi()
        .then(setStats)
        .catch(() => {});
    }
  }, [user]);

  if (!user) return null;

  const isStaff = user.role !== 'Requester';
  const isManagerOrAdmin = ['TeamLead', 'Manager', 'Administrator'].includes(user.role);

  const handleNavClick = (path: string) => {
    navigate(path);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="fixed top-0 w-full z-50 liquid-glass border-b border-outline-variant/35 shadow-sm">
        <div className="h-16 px-4 md:px-6 flex items-center justify-between gap-4 max-w-7xl mx-auto">
          {/* Left: Hamburger Button & Brand */}
          <div className="flex items-center gap-3 min-w-0">
            {/* Hamburger Toggle Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 -ml-1.5 rounded-lg hover:bg-surface-container text-on-surface-variant hover:text-on-surface flex items-center justify-center transition-all duration-200 press-tactile focus:outline-none"
              aria-label="Toggle navigation menu"
            >
              <span className="material-symbols-outlined text-[24px]">
                {mobileMenuOpen ? 'close' : 'menu'}
              </span>
            </button>

            {/* Brand Identity */}
            <div
              onClick={() => navigate('/')}
              className="flex items-center gap-2.5 cursor-pointer select-none min-w-0 group"
            >
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-base shadow-sm group-hover:scale-105 transition-transform duration-200">
                AI
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-mono text-[9px] text-primary tracking-widest uppercase font-semibold">
                  MW-OS // HELPDESK
                </span>
                <span className="font-headline text-sm md:text-base font-bold text-on-surface truncate group-hover:text-primary transition-colors">
                  AssistIQ Console
                </span>
              </div>
            </div>
          </div>

          {/* Center: Live Active Stats Pill (Staff Only) */}
          {stats && isStaff && (
            <div className="hidden lg:flex items-center gap-2.5 liquid-glass px-3.5 py-1.5 rounded-full border border-outline-variant/40 shadow-xs text-xs font-mono card-3d">
              <span className="flex items-center gap-1.5 text-on-surface">
                <span className="w-2.5 h-2.5 rounded-full bg-primary radar-live" />
                Active: <strong className="font-bold">{stats.active_cases}</strong>
              </span>
              <span className="text-outline-variant">|</span>
              <span className="text-secondary flex items-center gap-1">
                Breached: <strong className="font-bold">{stats.breached_cases}</strong>
              </span>
              <span className="text-outline-variant">|</span>
              <span className="text-tertiary flex items-center gap-1">
                Unassigned: <strong className="font-bold">{stats.unassigned_cases}</strong>
              </span>
            </div>
          )}

          {/* Right: User Profile & Account Actions */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 liquid-glass-interactive px-3 py-1.5 rounded-lg border border-outline-variant/40 press-tactile"
              >
                <div className="hidden sm:flex flex-col items-end text-right">
                  <span className="font-mono text-[11px] text-on-surface font-semibold truncate max-w-[130px]">
                    {user.email}
                  </span>
                  <span className="font-mono text-[9px] uppercase tracking-wider text-primary font-bold">
                    [{user.role}]
                  </span>
                </div>
                <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-on-primary text-xs font-bold shadow-xs">
                  {user.role[0]}
                </div>
                <span className={`material-symbols-outlined text-[16px] text-on-surface-variant transition-transform duration-200 ${showUserMenu ? 'rotate-180' : ''}`}>
                  expand_more
                </span>
              </button>

              {/* User Account Menu Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-64 liquid-glass-elevated border border-outline-variant/50 rounded-lg shadow-xl py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
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
                      className="w-full text-left px-3.5 py-2 text-xs text-error hover:bg-error-container/30 flex items-center gap-2 font-mono font-semibold transition-colors press-tactile"
                    >
                      <span className="material-symbols-outlined text-[16px]">logout</span>
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hamburger Slide-out Drawer Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex">
          {/* Backdrop Blur */}
          <div
            className="fixed inset-0 bg-inverse-surface/40 backdrop-blur-sm transition-opacity duration-300"
            onClick={() => setMobileMenuOpen(false)}
          />

          {/* Slide-out Sidebar Drawer */}
          <div className="relative w-80 max-w-[85vw] liquid-glass-elevated border-r border-outline-variant/40 h-full flex flex-col shadow-2xl z-10 animate-in slide-in-from-left duration-250">
            {/* Drawer Header */}
            <div className="h-16 px-5 flex items-center justify-between border-b border-outline-variant/30 bg-surface-container/60">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-sm shadow-xs">
                  AI
                </div>
                <div>
                  <span className="font-mono text-[9px] text-primary uppercase font-bold tracking-wider block">
                    NAVIGATION MENU
                  </span>
                  <span className="font-headline text-sm font-bold text-on-surface">
                    AssistIQ Helpdesk
                  </span>
                </div>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="w-8 h-8 rounded-lg hover:bg-surface-container-highest flex items-center justify-center text-on-surface-variant transition-all duration-200 press-tactile"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {/* User Info Card */}
            <div className="p-4 border-b border-outline-variant/30 bg-surface-container-lowest mx-3 my-3 rounded">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold text-sm">
                  {user.role[0]}
                </div>
                <div className="min-w-0">
                  <strong className="block text-xs font-mono text-on-surface truncate">
                    {user.email}
                  </strong>
                  <div className="flex items-center gap-1.5 mt-0.5 font-mono text-[10px]">
                    <span className="px-1.5 py-0.2 bg-primary/10 text-primary font-bold rounded">
                      {user.role}
                    </span>
                    {user.site && (
                      <span className="text-on-surface-variant truncate">
                        • {user.site}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="flex-1 px-3 py-2 space-y-1.5 overflow-y-auto font-mono text-xs">
              <button
                onClick={() => handleNavClick('/')}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-left hover:bg-surface-container-lowest text-on-surface transition-colors"
              >
                <span className="material-symbols-outlined text-primary text-[20px]">table_rows</span>
                <div>
                  <span className="font-bold block">{isStaff ? 'IT Workbench' : 'My Support Requests'}</span>
                  <span className="text-[10px] text-on-surface-variant font-sans">Queue & ticket management</span>
                </div>
              </button>

              {isManagerOrAdmin && (
                <button
                  onClick={() => handleNavClick('/insights')}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-left hover:bg-surface-container-lowest text-on-surface transition-colors"
                >
                  <span className="material-symbols-outlined text-primary text-[20px]">query_stats</span>
                  <div>
                    <span className="font-bold block">Operational Insights</span>
                    <span className="text-[10px] text-on-surface-variant font-sans">Metrics, trends & CSV exports</span>
                  </div>
                </button>
              )}

              {isStaff && (
                <button
                  onClick={() => handleNavClick('/dispatch')}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-left hover:bg-surface-container-lowest text-on-surface transition-colors"
                >
                  <span className="material-symbols-outlined text-secondary text-[20px]">notifications_active</span>
                  <div>
                    <span className="font-bold block">Dispatch & Alerts</span>
                    <span className="text-[10px] text-on-surface-variant font-sans">SLA breaches & human escalation</span>
                  </div>
                </button>
              )}

              <button
                onClick={() => handleNavClick('/knowledge')}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-left hover:bg-surface-container-lowest text-on-surface transition-colors"
              >
                <span className="material-symbols-outlined text-tertiary text-[20px]">menu_book</span>
                <div>
                  <span className="font-bold block">Knowledge Base</span>
                  <span className="text-[10px] text-on-surface-variant font-sans">SOPs, runbooks & unified search</span>
                </div>
              </button>

              {isStaff && (
                <button
                  onClick={() => handleNavClick('/admin')}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-left hover:bg-surface-container-lowest text-on-surface transition-colors"
                >
                  <span className="material-symbols-outlined text-primary text-[20px]">admin_panel_settings</span>
                  <div>
                    <span className="font-bold block">Administration & Audit</span>
                    <span className="text-[10px] text-on-surface-variant font-sans">User directory & RBAC scopes</span>
                  </div>
                </button>
              )}
            </div>

            {/* Drawer Footer Stats & Sign Out */}
            <div className="p-3 border-t border-outline-variant/30 space-y-2 bg-surface-container">
              {stats && isStaff && (
                <div className="p-2.5 bg-surface-container-lowest rounded border border-outline-variant/30 text-[11px] font-mono space-y-1">
                  <div className="flex justify-between text-on-surface">
                    <span>Active Cases:</span>
                    <strong className="text-primary">{stats.active_cases}</strong>
                  </div>
                  <div className="flex justify-between text-on-surface">
                    <span>SLA Breaches:</span>
                    <strong className="text-secondary">{stats.breached_cases}</strong>
                  </div>
                  <div className="flex justify-between text-on-surface">
                    <span>Unassigned:</span>
                    <strong className="text-tertiary">{stats.unassigned_cases}</strong>
                  </div>
                </div>
              )}

              <button
                onClick={() => {
                  logout();
                  setMobileMenuOpen(false);
                }}
                className="w-full py-2 px-3 bg-error/10 hover:bg-error/20 text-error font-mono text-xs font-bold rounded flex items-center justify-center gap-1.5 transition-colors"
              >
                <span className="material-symbols-outlined text-[16px]">logout</span>
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
