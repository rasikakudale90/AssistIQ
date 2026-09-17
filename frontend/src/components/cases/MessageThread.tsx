import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Message, CommunicationDraft } from '../../api/types';
import { listMessagesApi, postMessageApi, uploadAttachmentApi, getAttachmentDownloadUrl } from '../../api/messages';
import { createDraftApi, sendDraftApi } from '../../api/ai';

interface MessageThreadProps {
  caseId: string;
  onMessageSent?: () => void;
}

export const MessageThread: React.FC<MessageThreadProps> = ({ caseId, onMessageSent }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [body, setBody] = useState('');
  const [visibility, setVisibility] = useState<'requester_visible' | 'internal_only'>('requester_visible');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // AI Draft States
  const [draftModalOpen, setDraftModalOpen] = useState(false);
  const [draftType, setDraftType] = useState<'info_request' | 'progress_update' | 'resolution'>('info_request');
  const [generatedDraft, setGeneratedDraft] = useState<CommunicationDraft | null>(null);
  const [draftBody, setDraftBody] = useState('');
  const [draftSubject, setDraftSubject] = useState('');
  const [draftLoading, setDraftLoading] = useState(false);

  // File Upload
  const [uploadingFile, setUploadingFile] = useState(false);

  const isStaff = user && user.role !== 'Requester';

  const loadMessages = async () => {
    try {
      const data = await listMessagesApi(caseId);
      setMessages(data);
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMessages();
  }, [caseId]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim()) return;

    setSending(true);
    setError(null);
    try {
      await postMessageApi(caseId, {
        body,
        visibility: isStaff ? visibility : 'requester_visible',
      });
      setBody('');
      await loadMessages();
      if (onMessageSent) onMessageSent();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to post message');
    } finally {
      setSending(false);
    }
  };

  const handleGenerateDraft = async () => {
    setDraftLoading(true);
    try {
      const draft = await createDraftApi(caseId, draftType);
      setGeneratedDraft(draft);
      setDraftSubject(draft.subject);
      setDraftBody(draft.body);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to generate AI draft');
    } finally {
      setDraftLoading(false);
    }
  };

  const handleSendDraft = async () => {
    if (!generatedDraft) return;
    setDraftLoading(true);
    try {
      await sendDraftApi(generatedDraft.id, {
        subject: draftSubject,
        body: draftBody,
        visibility: 'requester_visible',
      });
      setDraftModalOpen(false);
      setGeneratedDraft(null);
      await loadMessages();
      if (onMessageSent) onMessageSent();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to send AI draft');
    } finally {
      setDraftLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];

    setUploadingFile(true);
    try {
      await uploadAttachmentApi(caseId, file);
      await loadMessages();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to upload attachment');
    } finally {
      setUploadingFile(false);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header & AI Draft Action Bar */}
      <div className="flex items-center justify-between border-b border-outline-variant/30 pb-2">
        <div className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-[18px] text-primary">forum</span>
          <span className="font-mono text-xs font-bold text-on-surface uppercase">
            Communication Thread ({messages.length})
          </span>
        </div>

        {isStaff && (
          <button
            type="button"
            onClick={() => {
              setDraftModalOpen(true);
              setGeneratedDraft(null);
            }}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-surface-container-high hover:bg-surface-container-highest rounded border border-outline-variant/40 text-xs font-mono text-primary font-bold transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">psychology</span>
            <span>AI Draft Assistant</span>
          </button>
        )}
      </div>

      {/* Messages List */}
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
        {loading ? (
          <div className="text-center py-6 font-mono text-xs text-on-surface-variant">
            Loading messages...
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-6 font-mono text-xs text-on-surface-variant italic bg-surface-container-low rounded">
            No messages recorded yet.
          </div>
        ) : (
          messages.map((m) => {
            const isInternal = m.visibility === 'internal_only';
            return (
              <div
                key={m.id}
                className={`p-3.5 rounded border ${
                  isInternal
                    ? 'bg-amber-50/70 border-tertiary/30'
                    : 'bg-surface-container-lowest border-outline-variant/30'
                } shadow-xs space-y-2`}
              >
                <div className="flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-on-surface">
                      {m.sender_email || 'Operator'}
                    </span>
                    {isInternal ? (
                      <span className="px-1.5 py-0.2 rounded bg-tertiary-container text-on-tertiary-container font-mono text-[9px] font-bold uppercase">
                        INTERNAL NOTE
                      </span>
                    ) : (
                      <span className="px-1.5 py-0.2 rounded bg-surface-container text-on-surface-variant font-mono text-[9px] uppercase">
                        PUBLIC
                      </span>
                    )}
                    {m.ai_generated && (
                      <span className="px-1.5 py-0.2 rounded bg-primary-fixed text-on-primary-fixed font-mono text-[9px] font-bold flex items-center gap-1">
                        <span className="material-symbols-outlined text-[10px]">auto_awesome</span>
                        AI DRAFTED
                      </span>
                    )}
                  </div>
                  <span className="font-mono text-[10px] text-on-surface-variant">
                    {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <p className="text-xs text-on-surface font-sans leading-relaxed whitespace-pre-wrap">
                  {m.body}
                </p>

                {/* Attachments */}
                {m.attachments && m.attachments.length > 0 && (
                  <div className="pt-2 border-t border-outline-variant/20 flex flex-wrap gap-2">
                    {m.attachments.map((att) => (
                      <a
                        key={att.id}
                        href={getAttachmentDownloadUrl(att.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-2 py-1 bg-surface-container rounded border border-outline-variant/30 text-[11px] font-mono text-primary hover:underline"
                      >
                        <span className="material-symbols-outlined text-[14px]">attachment</span>
                        <span>{att.file_name}</span>
                        <span className="text-on-surface-variant text-[9px]">
                          ({Math.round(att.file_size / 1024)} KB)
                        </span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Post Message Input Form */}
      <form onSubmit={handleSendMessage} className="space-y-2 pt-2 border-t border-outline-variant/30">
        {error && (
          <div className="p-2 bg-error-container text-on-error-container text-xs rounded">
            {error}
          </div>
        )}

        {isStaff && (
          <div className="flex items-center gap-4 text-xs font-mono">
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="radio"
                name="visibility"
                checked={visibility === 'requester_visible'}
                onChange={() => setVisibility('requester_visible')}
                className="accent-primary"
              />
              <span className="text-on-surface">Public Note (Requester visible)</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer text-tertiary">
              <input
                type="radio"
                name="visibility"
                checked={visibility === 'internal_only'}
                onChange={() => setVisibility('internal_only')}
                className="accent-tertiary"
              />
              <span className="font-semibold">Internal Note Only</span>
            </label>
          </div>
        )}

        <div className="relative">
          <textarea
            rows={3}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder={
              visibility === 'internal_only'
                ? 'Add internal investigation notes, telemetry findings, or operator handoff logs...'
                : 'Write a response to the requester...'
            }
            className={`w-full p-2.5 rounded border text-xs text-on-surface focus:outline-none ${
              visibility === 'internal_only'
                ? 'bg-amber-50/50 border-tertiary/40 focus:ring-1 focus:ring-tertiary'
                : 'bg-surface-container-lowest border-outline-variant/40 focus:ring-1 focus:ring-primary'
            }`}
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-1.5 cursor-pointer text-xs font-mono text-on-surface-variant hover:text-on-surface">
            <span className="material-symbols-outlined text-[16px]">attach_file</span>
            <span>{uploadingFile ? 'Uploading...' : 'Attach File'}</span>
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploadingFile}
              className="hidden"
            />
          </label>

          <button
            type="submit"
            disabled={sending || !body.trim()}
            className="px-4 py-1.5 bg-primary hover:bg-primary-container disabled:opacity-50 text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[14px]">send</span>
            <span>{sending ? 'Posting...' : 'Post Note'}</span>
          </button>
        </div>
      </form>

      {/* AI Draft Review & Send Modal */}
      {draftModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-inverse-surface/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface-container-high rounded-lg max-w-xl w-full p-5 shadow-xl border border-outline-variant/40 space-y-4">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-2">
              <div className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
                <span className="font-mono text-xs text-primary font-bold uppercase">
                  AI Communication Draft Assistant (SRS §5.9)
                </span>
              </div>
              <button
                onClick={() => setDraftModalOpen(false)}
                className="w-7 h-7 rounded hover:bg-surface-container flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[16px]">close</span>
              </button>
            </div>

            {!generatedDraft ? (
              <div className="space-y-3">
                <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase">
                  Select Draft Objective
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setDraftType('info_request')}
                    className={`p-3 rounded border text-left text-xs font-mono transition-colors ${
                      draftType === 'info_request'
                        ? 'bg-primary text-on-primary border-primary font-bold'
                        : 'bg-surface-container-lowest border-outline-variant/30 text-on-surface hover:bg-surface-container'
                    }`}
                  >
                    <span className="block font-bold">Clarification</span>
                    <span className="text-[10px] opacity-80">Request missing info</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setDraftType('progress_update')}
                    className={`p-3 rounded border text-left text-xs font-mono transition-colors ${
                      draftType === 'progress_update'
                        ? 'bg-primary text-on-primary border-primary font-bold'
                        : 'bg-surface-container-lowest border-outline-variant/30 text-on-surface hover:bg-surface-container'
                    }`}
                  >
                    <span className="block font-bold">Progress</span>
                    <span className="text-[10px] opacity-80">Status milestone update</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setDraftType('resolution')}
                    className={`p-3 rounded border text-left text-xs font-mono transition-colors ${
                      draftType === 'resolution'
                        ? 'bg-primary text-on-primary border-primary font-bold'
                        : 'bg-surface-container-lowest border-outline-variant/30 text-on-surface hover:bg-surface-container'
                    }`}
                  >
                    <span className="block font-bold">Resolution</span>
                    <span className="text-[10px] opacity-80">Root cause & fix</span>
                  </button>
                </div>

                <div className="flex justify-end pt-3">
                  <button
                    type="button"
                    onClick={handleGenerateDraft}
                    disabled={draftLoading}
                    className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors flex items-center gap-1.5 uppercase"
                  >
                    <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
                    {draftLoading ? 'Generating Draft...' : 'Generate with Gemini'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="p-2 bg-primary-fixed text-on-primary-fixed rounded text-xs font-mono flex items-center justify-between">
                  <span>AI Draft Generated — Review & Edit before sending</span>
                  <span className="font-bold">STATUS: DRAFT</span>
                </div>

                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                    Subject Line
                  </label>
                  <input
                    type="text"
                    value={draftSubject}
                    onChange={(e) => setDraftSubject(e.target.value)}
                    className="w-full px-3 py-1.5 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
                  />
                </div>

                <div>
                  <label className="block font-mono text-[11px] font-semibold text-on-surface-variant uppercase mb-1">
                    Draft Message Body
                  </label>
                  <textarea
                    rows={6}
                    value={draftBody}
                    onChange={(e) => setDraftBody(e.target.value)}
                    className="w-full p-3 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-sans"
                  />
                </div>

                <div className="flex justify-between items-center pt-2 border-t border-outline-variant/20">
                  <button
                    type="button"
                    onClick={() => setGeneratedDraft(null)}
                    className="px-3 py-1.5 bg-surface-container text-on-surface font-mono text-xs rounded hover:bg-surface-container-highest"
                  >
                    Back
                  </button>

                  <button
                    type="button"
                    onClick={handleSendDraft}
                    disabled={draftLoading}
                    className="px-4 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs flex items-center gap-1.5 uppercase"
                  >
                    <span className="material-symbols-outlined text-[14px]">send</span>
                    {draftLoading ? 'Sending...' : 'Approve & Send to Requester'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
