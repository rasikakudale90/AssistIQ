import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';

interface DownloadInfo {
  version: string;
  local_ip: string;
  desktop: {
    available: boolean;
    filename: string;
    size_mb: number;
    download_url: string;
    lan_download_url: string;
    platform: string;
  };
  android: {
    available: boolean;
    filename: string;
    size_mb: number;
    download_url: string;
    lan_download_url: string;
    platform: string;
  };
  ios: {
    available: boolean;
    type: string;
    platform: string;
  };
}

interface ClientInstallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ClientInstallModal: React.FC<ClientInstallModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'desktop' | 'android' | 'ios'>('desktop');
  const [info, setInfo] = useState<DownloadInfo | null>(null);
  const [pwaPrompt, setPwaPrompt] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      apiClient
        .get('/downloads/info')
        .then((res) => setInfo(res.data))
        .catch(() => {
          // Fallback defaults
          setInfo({
            version: '1.0.0',
            local_ip: window.location.hostname || '127.0.0.1',
            desktop: {
              available: true,
              filename: 'AssistIQ-Helpdesk-Setup.exe',
              size_mb: 112.8,
              download_url: '/api/v1/downloads/desktop',
              lan_download_url: `http://${window.location.hostname || '127.0.0.1'}:8000/api/v1/downloads/desktop`,
              platform: 'Windows 10/11 (64-bit)',
            },
            android: {
              available: true,
              filename: 'AssistIQ-Mobile.apk',
              size_mb: 70.4,
              download_url: '/api/v1/downloads/android',
              lan_download_url: `http://${window.location.hostname || '127.0.0.1'}:8000/api/v1/downloads/android`,
              platform: 'Android 10+ (ARM64/x86)',
            },
            ios: {
              available: true,
              type: 'PWA',
              platform: 'iOS Safari / iPadOS',
            },
          });
        });
    }

    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setPwaPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleTriggerPwa = async () => {
    if (pwaPrompt) {
      pwaPrompt.prompt();
      const choice = await pwaPrompt.userChoice;
      if (choice.outcome === 'accepted') {
        setPwaPrompt(null);
      }
    }
  };

  const getAndroidDownloadUrl = () => {
    if (info?.android.lan_download_url) return info.android.lan_download_url;
    const host = window.location.hostname || '127.0.0.1';
    return `http://${host}:8000/api/v1/downloads/android`;
  };

  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(
    getAndroidDownloadUrl()
  )}&margin=10&color=111827&bgcolor=ffffff`;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-inverse-surface/60 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
      <div className="liquid-glass-elevated rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-outline-variant/40 space-y-5 animate-scaleUp">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-3.5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center text-primary shadow-xs">
              <span className="material-symbols-outlined text-[24px]">download_for_offline</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-headline font-bold text-base text-on-surface">
                  AssistIQ Multi-Platform Client Hub
                </h3>
                <span className="px-2 py-0.5 rounded-full font-mono text-[10px] font-bold bg-primary/20 text-primary border border-primary/30">
                  v1.0.0
                </span>
              </div>
              <p className="text-xs text-on-surface-variant font-sans mt-0.5">
                Install native desktop applications and mobile packages across all devices
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-surface-container flex items-center justify-center text-on-surface-variant hover:text-on-surface press-tactile transition-colors"
            title="Close"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Platform Selector Tabs */}
        <div className="grid grid-cols-3 gap-2 p-1.5 bg-surface-container-lowest/80 dark:bg-surface-container-lowest/40 rounded-xl border border-outline-variant/30">
          <button
            onClick={() => setActiveTab('desktop')}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-mono font-bold transition-all ${
              activeTab === 'desktop'
                ? 'bg-primary text-on-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">desktop_windows</span>
            <span>Windows PC</span>
          </button>

          <button
            onClick={() => setActiveTab('android')}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-mono font-bold transition-all ${
              activeTab === 'android'
                ? 'bg-primary text-on-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">phone_android</span>
            <span>Android Phone</span>
          </button>

          <button
            onClick={() => setActiveTab('ios')}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-mono font-bold transition-all ${
              activeTab === 'ios'
                ? 'bg-primary text-on-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">phone_iphone</span>
            <span>iOS / PWA</span>
          </button>
        </div>

        {/* Tab 1: Windows Desktop */}
        {activeTab === 'desktop' && (
          <div className="space-y-4 animate-fadeIn">
            <div className="p-4 bg-surface-container-lowest/80 dark:bg-surface-container-low/70 rounded-xl border border-outline-variant/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="w-12 h-12 rounded-xl bg-primary text-on-primary flex items-center justify-center shrink-0 shadow-md">
                  <span className="material-symbols-outlined text-2xl">laptop_windows</span>
                </div>
                <div>
                  <h4 className="font-headline font-bold text-sm text-on-surface">
                    AssistIQ Helpdesk for Windows
                  </h4>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Official 64-bit installer with Start Menu integration & Desktop shortcuts.
                  </p>
                  <div className="flex flex-wrap items-center gap-2 mt-2 text-[11px] font-mono text-on-surface-variant">
                    <span className="px-2 py-0.5 bg-surface-container rounded border border-outline-variant/20">
                      📦 Size: ~{info?.desktop.size_mb || 107.6} MB
                    </span>
                    <span className="px-2 py-0.5 bg-surface-container rounded border border-outline-variant/20">
                      💻 Windows 10/11 (64-bit)
                    </span>
                  </div>
                </div>
              </div>

              <a
                href={info?.desktop.download_url || '/api/v1/downloads/desktop'}
                download="AssistIQ-Helpdesk-Setup.exe"
                className="w-full sm:w-auto px-5 py-2.5 bg-primary hover:bg-primary/90 text-on-primary font-mono text-xs font-bold rounded-xl shadow-md press-tactile transition-all flex items-center justify-center gap-2 shrink-0"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                <span>Download .EXE</span>
              </a>
            </div>

            {/* Quick Steps */}
            <div className="p-4 bg-surface-container-lowest/50 dark:bg-surface-container-low/40 rounded-xl border border-outline-variant/30 space-y-2.5 text-xs text-on-surface">
              <span className="font-mono text-[11px] font-bold text-primary uppercase tracking-wider block">
                Installation Instructions (3 Easy Steps):
              </span>
              <ol className="list-decimal list-inside space-y-1.5 text-on-surface-variant font-sans leading-relaxed">
                <li>Click <strong>Download .EXE</strong> above to download the installer setup wizard.</li>
                <li>Run <code className="px-1.5 py-0.5 bg-surface-container rounded text-primary font-mono text-[11px]">AssistIQ Helpdesk Setup 1.0.0.exe</code> and click <strong>Install</strong>.</li>
                <li>Launch <strong>AssistIQ Helpdesk</strong> from your Desktop or Start Menu.</li>
              </ol>
            </div>
          </div>
        )}

        {/* Tab 2: Android Phone */}
        {activeTab === 'android' && (
          <div className="space-y-4 animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* QR Code Scanner Card */}
              <div className="p-4 bg-surface-container-lowest/80 dark:bg-surface-container-low/70 rounded-xl border border-outline-variant/30 flex flex-col items-center text-center space-y-3">
                <span className="font-mono text-xs font-bold text-primary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[16px]">qr_code_scanner</span>
                  Scan Camera to Install
                </span>
                <div className="p-3 bg-white rounded-xl shadow-md border border-outline-variant/30">
                  <img
                    src={qrCodeUrl}
                    alt="Scan to Install Android APK"
                    className="w-36 h-36 object-contain rounded-lg"
                  />
                </div>
                <span className="text-[11px] text-on-surface-variant font-sans">
                  Point phone camera at screen to download APK directly over Wi-Fi
                </span>
              </div>

              {/* Direct APK Download Card */}
              <div className="p-4 bg-surface-container-lowest/80 dark:bg-surface-container-low/70 rounded-xl border border-outline-variant/30 flex flex-col justify-between space-y-3">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-secondary text-on-secondary flex items-center justify-center shadow-xs">
                    <span className="material-symbols-outlined text-xl">android</span>
                  </div>
                  <h4 className="font-headline font-bold text-sm text-on-surface">
                    Direct APK Package
                  </h4>
                  <p className="text-xs text-on-surface-variant">
                    Optimized Release Build with AOT fast startup & tree-shaken assets.
                  </p>
                  <div className="flex flex-col gap-1.5 text-[11px] font-mono text-on-surface-variant pt-1">
                    <span className="px-2 py-0.5 bg-surface-container rounded border border-outline-variant/20 inline-block w-fit">
                      📦 Size: ~{info?.android.size_mb || 50.2} MB
                    </span>
                    <span className="px-2 py-0.5 bg-surface-container rounded border border-outline-variant/20 inline-block w-fit">
                      📱 Target: Android 10+ (ARM64)
                    </span>
                  </div>
                </div>

                <a
                  href={info?.android.download_url || '/api/v1/downloads/android'}
                  download="AssistIQ-Mobile.apk"
                  className="w-full px-4 py-2.5 bg-secondary hover:bg-secondary/90 text-on-secondary font-mono text-xs font-bold rounded-xl shadow-md press-tactile transition-all flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  <span>Download .APK</span>
                </a>
              </div>
            </div>

            {/* Quick Sideload Tip */}
            <div className="p-3.5 bg-surface-container-lowest/70 dark:bg-surface-container-low/70 rounded-xl border border-secondary/30 flex items-start gap-2.5 text-xs text-on-surface">
              <span className="material-symbols-outlined text-secondary text-[18px] shrink-0 mt-0.5">info</span>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                If prompted on your phone, tap <strong className="text-on-surface">"Allow installation from this source"</strong> in Android settings to complete installation.
              </p>
            </div>
          </div>
        )}

        {/* Tab 3: iOS & PWA */}
        {activeTab === 'ios' && (
          <div className="space-y-4 animate-fadeIn">
            <div className="p-4 bg-surface-container-lowest/80 dark:bg-surface-container-low/70 rounded-xl border border-outline-variant/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="w-12 h-12 rounded-xl bg-tertiary text-on-tertiary flex items-center justify-center shrink-0 shadow-md">
                  <span className="material-symbols-outlined text-2xl">install_mobile</span>
                </div>
                <div>
                  <h4 className="font-headline font-bold text-sm text-on-surface">
                    Progressive Web App (PWA)
                  </h4>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Zero download required. Runs full-screen with offline caching on iPhone, iPad, & Mac.
                  </p>
                </div>
              </div>

              {pwaPrompt ? (
                <button
                  onClick={handleTriggerPwa}
                  className="px-5 py-2.5 bg-tertiary hover:bg-tertiary/90 text-on-tertiary font-mono text-xs font-bold rounded-xl shadow-md press-tactile transition-all flex items-center justify-center gap-2 shrink-0"
                >
                  <span className="material-symbols-outlined text-[18px]">add_to_home_screen</span>
                  <span>Install Web App</span>
                </button>
              ) : (
                <span className="px-3 py-1.5 bg-surface-container text-on-surface font-mono text-xs rounded-lg border border-outline-variant/30">
                  Ready in Browser
                </span>
              )}
            </div>

            {/* iOS Safari Instructions */}
            <div className="p-4 bg-surface-container-lowest/50 dark:bg-surface-container-low/40 rounded-xl border border-outline-variant/30 space-y-2 text-xs text-on-surface">
              <span className="font-mono text-[11px] font-bold text-tertiary uppercase tracking-wider block">
                How to Install on iPhone / iPad Safari:
              </span>
              <ol className="list-decimal list-inside space-y-1.5 text-on-surface-variant font-sans leading-relaxed">
                <li>Open <strong>AssistIQ</strong> in Safari on your iPhone/iPad.</li>
                <li>Tap the <strong>Share</strong> button (box with an arrow pointing up).</li>
                <li>Scroll down and tap <strong>"Add to Home Screen"</strong>.</li>
                <li>Tap <strong>Add</strong> in the top-right corner to launch AssistIQ as a native app!</li>
              </ol>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center pt-3.5 border-t border-outline-variant/30 text-xs text-on-surface-variant">
          <span className="font-mono text-[11px]">
            Backend API: <strong className="text-primary">{info?.local_ip || '127.0.0.1'}:8000</strong>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-surface-container hover:bg-surface-container-high text-on-surface font-mono text-xs rounded-lg press-tactile border border-outline-variant/20 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
