import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, UserRole } from '../api/types';
import { loginApi, getMeApi } from '../api/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  switchDemoRole: (role: UserRole) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEMO_USERS: Record<UserRole, string> = {
  Requester: 'requester@assistiq.local',
  Operator: 'operator@assistiq.local',
  TeamLead: 'lead@assistiq.local',
  Manager: 'manager@assistiq.local',
  Administrator: 'admin@assistiq.local',
};

const DEMO_PASSWORD = 'Password123!@#';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem('assistiq_token');
      if (token) {
        try {
          const u = await getMeApi();
          setUser(u);
        } catch {
          localStorage.removeItem('assistiq_token');
          localStorage.removeItem('assistiq_user');
          setUser(null);
        }
      }
      setLoading(false);
    }
    loadUser();
  }, []);

  const login = async (email: string, pass: string) => {
    setLoading(true);
    try {
      const { user: u } = await loginApi(email, pass);
      setUser(u);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('assistiq_token');
    localStorage.removeItem('assistiq_refresh_token');
    localStorage.removeItem('assistiq_user');
    setUser(null);
  };

  const switchDemoRole = async (role: UserRole) => {
    const email = DEMO_USERS[role];
    await login(email, DEMO_PASSWORD);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, switchDemoRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
