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
    <div className="min-h-screen bg-surface flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-12 h-12 rounded bg-primary flex items-center justify-center text-on-primary font-headline font-bold text-2xl mx-auto shadow-md">
          AI
        </div>
        <h2 className="mt-4 font-headline text-2xl font-bold text-on-surface">
          AssistIQ Enterprise Helpdesk
        </h2>
        <p className="mt-1 font-mono text-xs text-primary font-medium tracking-wider uppercase">
          MW-OS // SECURE WORKSTATION ACCESS
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-surface-container-high py-6 px-6 shadow-sm rounded-lg border border-outline-variant/30 space-y-4">
          {/* Sign In vs Register Tabs */}
          <div className="grid grid-cols-2 gap-1 bg-surface-container-lowest p-1 rounded border border-outline-variant/30 text-xs font-mono">
            <button
              type="button"
              onClick={() => {
                setAuthMode('signin');
                setError(null);
              }}
              className={`py-2 rounded font-bold transition-colors ${
                authMode === 'signin'
                  ? 'bg-primary text-on-primary shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
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
              className={`py-2 rounded font-bold transition-colors ${
                authMode === 'register'
                  ? 'bg-primary text-on-primary shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              REGISTER ACCOUNT
            </button>
          </div>

          {/* Alert Messages */}
          {error && (
            <div className="p-3 bg-error-container text-on-error-container text-xs rounded border border-error/20 flex items-start gap-2">
              <span className="material-symbols-outlined text-[16px] text-error mt-0.5">error</span>
              <span>{error}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3 bg-emerald-50 text-emerald-800 text-xs rounded border border-emerald-300 flex items-start gap-2">
              <span className="material-symbols-outlined text-[16px] text-emerald-600 mt-0.5">check_circle</span>
              <span>{successMessage}</span>
            </div>
          )}

          {authMode === 'signin' ? (
            /* Sign In Form */
            <form className="space-y-3.5" onSubmit={handleSignIn}>
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Corporate Email
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@assistiq.local"
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors uppercase tracking-wider flex items-center justify-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[16px]">login</span>
                <span>{loading ? 'Authenticating...' : 'Sign In to Console'}</span>
              </button>
            </form>
          ) : (
            /* Register Account Form */
            <form className="space-y-3.5" onSubmit={handleRegister}>
              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Corporate Email
                </label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="name@company.local"
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
              </div>

              <div>
                <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                  Create Password (Min 12 Characters)
                </label>
                <input
                  type="password"
                  required
                  minLength={12}
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Min 12 characters (e.g. Password123!@#)"
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
                <span className="text-[10px] text-on-surface-variant block mt-0.5">
                  Must meet enterprise Argon2id complexity requirements.
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                    Role
                  </label>
                  <select
                    value={regRole}
                    onChange={(e) => setRegRole(e.target.value as UserRole)}
                    className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
                  >
                    <option value="Requester">Requester</option>
                    <option value="Operator">Operator</option>
                    <option value="TeamLead">TeamLead</option>
                    <option value="Manager">Manager</option>
                    <option value="Administrator">Administrator</option>
                  </select>
                </div>

                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                    Facility / Site
                  </label>
                  <input
                    type="text"
                    value={regSite}
                    onChange={(e) => setRegSite(e.target.value)}
                    placeholder="e.g. Main Facility"
                    className="w-full px-2.5 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={regLoading}
                className="w-full mt-2 py-2.5 px-4 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors uppercase tracking-wider flex items-center justify-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[16px]">person_add</span>
                <span>{regLoading ? 'Registering Account...' : 'Create Account'}</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
