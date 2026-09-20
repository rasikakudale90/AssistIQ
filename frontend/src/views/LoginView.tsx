import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { signupApi } from '../api/auth';
import { UserRole } from '../api/types';

export const LoginView: React.FC = () => {
  const { login, loading } = useAuth();
  const [authMode, setAuthMode] = useState<'signin' | 'register'>('signin');

  // Sign In States
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Register States
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState<UserRole>('Requester');
  const [regSite, setRegSite] = useState('Main Facility');
  const [regLoading, setRegLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.message || err.response?.data?.error?.message || err.message || 'Invalid email or password');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (regPassword.length < 12) {
      setError('Password must be at least 12 characters long per enterprise security policy (SRS §7.4).');
      return;
    }

    setRegLoading(true);
    try {
      await signupApi(regEmail, regPassword, regRole, regSite);
      setSuccessMessage('Account registered successfully! You can now sign in with your credentials.');
      setEmail(regEmail);
      setPassword('');
      setAuthMode('signin');
    } catch (err: any) {
      setError(err.response?.data?.message || err.response?.data?.error?.message || err.message || 'Registration failed. Email might already exist.');
    } finally {
      setRegLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="relative inline-flex items-center justify-center">
          <div className="w-14 h-14 rounded-2xl bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-2xl shadow-xl card-3d">
            AI
          </div>
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-secondary radar-live" />
        </div>
        <h2 className="mt-4 font-headline text-2xl font-bold text-on-surface">
          AssistIQ Enterprise Helpdesk
        </h2>
        <p className="mt-1 font-mono text-xs text-primary font-bold tracking-wider uppercase flex items-center justify-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          MW-OS // SECURE WORKSTATION ACCESS
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="liquid-glass-elevated py-7 px-7 shadow-2xl rounded-2xl border border-outline-variant/40 space-y-5">
          {/* Sign In vs Register Tabs */}
          <div className="grid grid-cols-2 gap-1 bg-surface-container-lowest/80 backdrop-blur-md p-1 rounded-xl border border-outline-variant/30 text-xs font-mono shadow-xs">
            <button
              type="button"
              onClick={() => {
                setAuthMode('signin');
                setError(null);
              }}
              className={`py-2 rounded-lg font-bold transition-all press-tactile ${
                authMode === 'signin'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/40'
              }`}
            >
              SIGN IN
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('register');
                setError(null);
                setSuccessMessage(null);
              }}
              className={`py-2 rounded-lg font-bold transition-all press-tactile ${
                authMode === 'register'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/40'
              }`}
            >
              REGISTER ACCOUNT
            </button>
          </div>

          {/* Alert Messages */}
          {error && (
            <div className="p-3.5 bg-error-container/80 backdrop-blur-xs text-on-error-container text-xs rounded-xl border border-error/30 flex items-start gap-2 shadow-xs animate-shake">
              <span className="material-symbols-outlined text-[16px] text-error mt-0.5">error</span>
              <span>{error}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3.5 bg-emerald-500/10 backdrop-blur-xs text-primary text-xs rounded-xl border border-primary/30 flex items-start gap-2 shadow-xs animate-fadeIn">
              <span className="material-symbols-outlined text-[16px] text-primary mt-0.5">check_circle</span>
              <span>{successMessage}</span>
            </div>
          )}

          {authMode === 'signin' ? (
            /* Sign In Form */
            <form className="space-y-4" onSubmit={handleSignIn}>
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Corporate Email
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@assistiq.local"
                  className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface input-liquid focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface input-liquid focus:outline-none font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-xl shadow-md press-tactile transition-all uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <span className={`material-symbols-outlined text-[16px] ${loading ? 'animate-spin' : ''}`}>
                  {loading ? 'sync' : 'login'}
                </span>
                <span>{loading ? 'Authenticating...' : 'Sign In to Console'}</span>
              </button>
            </form>
          ) : (
            /* Register Account Form */
            <form className="space-y-4" onSubmit={handleRegister}>
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Corporate Email
                </label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="name@company.local"
                  className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface input-liquid focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                  Create Password (Min 12 Characters)
                </label>
                <input
                  type="password"
                  required
                  minLength={12}
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Min 12 characters (e.g. Password123!@#)"
                  className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface input-liquid focus:outline-none font-mono"
                />
                <span className="text-[10px] text-on-surface-variant block mt-1">
                  Must meet enterprise Argon2id complexity requirements.
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                    Role
                  </label>
                  <select
                    value={regRole}
                    onChange={(e) => setRegRole(e.target.value as UserRole)}
                    className="w-full px-3 py-2 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface font-mono input-liquid focus:outline-none"
                  >
                    <option value="Requester">Requester</option>
                    <option value="Operator">Operator</option>
                    <option value="TeamLead">TeamLead</option>
                    <option value="Manager">Manager</option>
                    <option value="Administrator">Administrator</option>
                  </select>
                </div>

                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                    Facility / Site
                  </label>
                  <input
                    type="text"
                    value={regSite}
                    onChange={(e) => setRegSite(e.target.value)}
                    placeholder="e.g. Main Facility"
                    className="w-full px-3 py-2 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface font-mono input-liquid focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={regLoading}
                className="w-full mt-2 py-3 px-4 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-xl shadow-md press-tactile transition-all uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <span className={`material-symbols-outlined text-[16px] ${regLoading ? 'animate-spin' : ''}`}>
                  {regLoading ? 'sync' : 'person_add'}
                </span>
                <span>{regLoading ? 'Registering Account...' : 'Create Account'}</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
