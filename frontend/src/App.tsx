import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Header } from './components/layout/Header';
import { Navigation } from './components/layout/Navigation';
import { LoginView } from './views/LoginView';
import { WorkbenchView } from './views/WorkbenchView';
import { InsightsView } from './views/InsightsView';
import { DispatchView } from './views/DispatchView';
import { KnowledgeView } from './views/KnowledgeView';
import { AdminView } from './views/AdminView';

const MainLayout: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center font-mono text-xs text-primary font-bold">
        Loading AssistIQ Workbench...
      </div>
    );
  }

  if (!user) {
    return <LoginView />;
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col font-sans text-on-surface transition-colors duration-300">
      <Header />
      <div className="pt-16">
        <Navigation />
        <main className="flex-1 pb-16">
          <Routes>
            <Route path="/" element={<WorkbenchView />} />
            <Route path="/insights" element={<InsightsView />} />
            <Route path="/dispatch" element={<DispatchView />} />
            <Route path="/knowledge" element={<KnowledgeView />} />
            <Route path="/admin" element={<AdminView />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <MainLayout />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};
