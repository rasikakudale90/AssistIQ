import { apiClient } from './client';
import { Message, Attachment } from './types';

export async function listMessagesApi(caseId: string): Promise<Message[]> {
  const res = await apiClient.get<any>(`/cases/${caseId}/messages`);
  const rawList = Array.isArray(res.data) ? res.data : (res.data?.items || []);
  return rawList.map((m: any) => ({
    ...m,
    sender_email: m.author?.email || m.sender_email || (m.visibility === 'internal_only' ? 'Staff Internal' : 'Support Desk'),
  }));
}

export async function postMessageApi(
  caseId: string,
  payload: { body: string; visibility: 'requester_visible' | 'internal_only' }
): Promise<Message> {
  const res = await apiClient.post<Message>(`/cases/${caseId}/messages`, payload);
  return res.data;
}

export async function listAttachmentsApi(caseId: string): Promise<Attachment[]> {
  const res = await apiClient.get<any>(`/cases/${caseId}/attachments`);
  const rawList = Array.isArray(res.data) ? res.data : (res.data?.items || []);
  return rawList;
}

export async function uploadAttachmentApi(caseId: string, file: File): Promise<Attachment> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await apiClient.post<Attachment>(`/cases/${caseId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function downloadAttachmentBlob(caseId: string, attachmentId: string, fileName: string): Promise<void> {
  const res = await apiClient.get(`/cases/${caseId}/attachments/${attachmentId}/download`, {
    responseType: 'blob',
  });
  const blobUrl = window.URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(blobUrl);
}

export function getAttachmentDownloadUrl(caseId: string, attachmentId: string): string {
  return `/api/v1/cases/${caseId}/attachments/${attachmentId}/download`;
}

