import { apiClient } from './client';
import { Message, Attachment } from './types';

export async function listMessagesApi(caseId: string): Promise<Message[]> {
  const res = await apiClient.get<Message[]>(`/cases/${caseId}/messages`);
  return res.data;
}

export async function postMessageApi(
  caseId: string,
  payload: { body: string; visibility: 'requester_visible' | 'internal_only' }
): Promise<Message> {
  const res = await apiClient.post<Message>(`/cases/${caseId}/messages`, payload);
  return res.data;
}

export async function uploadAttachmentApi(caseId: string, file: File, messageId?: string): Promise<Attachment> {
  const formData = new FormData();
  formData.append('file', file);
  if (messageId) {
    formData.append('message_id', messageId);
  }

  const res = await apiClient.post<Attachment>(`/cases/${caseId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export function getAttachmentDownloadUrl(attachmentId: string): string {
  return `/api/v1/attachments/${attachmentId}/download`;
}
