import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Navigation: React.FC = () => {
  const { user } = useAuth();
  if (!user) return null;

  const isStaff = user.role !== 'Requester';
  const isManagerOrAdmin = ['TeamLead', 'Manager', 'Administrator'].includes(user.role);

  return (
    <nav className="liquid-glass border-b border-outline-variant/30 px-4 md:px-6 sticky top-16 z-40">
      <div className="max-w-7xl mx-auto flex items-center gap-2 overflow-x-auto py-2.5">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 press-tactile ${
              isActive
                ? 'bg-primary text-on-primary font-bold shadow-sm scale-[1.02]'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/80'
            }`
          }
        >
          <span className="material-symbols-outlined text-[16px]">table_rows</span>
          <span>{isStaff ? 'WORKBENCH' : 'MY CASES'}</span>
        </NavLink>

        {isManagerOrAdmin && (
          <NavLink
            to="/insights"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 press-tactile ${
                isActive
                  ? 'bg-primary text-on-primary font-bold shadow-sm scale-[1.02]'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/80'
              }`
            }
          >
            <span className="material-symbols-outlined text-[16px]">query_stats</span>
            <span>OPERATIONAL INSIGHTS</span>
          </NavLink>
        )}

        {isStaff && (
          <NavLink
            to="/dispatch"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 press-tactile ${
                isActive
                  ? 'bg-primary text-on-primary font-bold shadow-sm scale-[1.02]'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/80'
              }`
            }
          >
            <span className="material-symbols-outlined text-[16px]">notifications_active</span>
            <span>DISPATCH & ALERTS</span>
          </NavLink>
        )}

        <NavLink
          to="/knowledge"
          className={({ isActive }) =>
            `flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 press-tactile ${
              isActive
                ? 'bg-primary text-on-primary font-bold shadow-sm scale-[1.02]'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/80'
            }`
          }
        >
          <span className="material-symbols-outlined text-[16px]">menu_book</span>
          <span>KNOWLEDGE BASE</span>
        </NavLink>

        {isStaff && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 press-tactile ${
                isActive
                  ? 'bg-primary text-on-primary font-bold shadow-sm scale-[1.02]'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/80'
              }`
            }
          >
            <span className="material-symbols-outlined text-[16px]">admin_panel_settings</span>
            <span>SYSTEM & AUDIT</span>
          </NavLink>
        )}
      </div>
    </nav>
  );
};
