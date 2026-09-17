import { apiClient } from './client';
import { AITriageResult, CaseSummary, RiskAssessment, CommunicationDraft } from './types';

export async function getCaseTriageApi(caseId: string): Promise<AITriageResult> {
  const res = await apiClient.get<AITriageResult>(`/cases/${caseId}/triage`);
  return res.data;
}

export async function getCaseSummaryApi(caseId: string): Promise<CaseSummary> {
  const res = await apiClient.get<CaseSummary>(`/cases/${caseId}/summary`);
  return res.data;
}

export async function getCaseRiskApi(caseId: string): Promise<RiskAssessment> {
  const res = await apiClient.get<RiskAssessment>(`/cases/${caseId}/risk`);
  return res.data;
}

export async function getAssignmentRecommendationsApi(caseId: string): Promise<any> {
  const res = await apiClient.get(`/cases/${caseId}/assignment-recommendations`);
  return res.data;
}

export async function createDraftApi(
  caseId: string,
  draftType: 'info_request' | 'progress_update' | 'resolution' | 'escalation_summary'
): Promise<CommunicationDraft> {
  const res = await apiClient.post<CommunicationDraft>(`/cases/${caseId}/drafts`, { draft_type: draftType });
  return res.data;
}

export async function listDraftsApi(caseId: string): Promise<CommunicationDraft[]> {
  const res = await apiClient.get<CommunicationDraft[]>(`/cases/${caseId}/drafts`);
  return res.data;
}

export async function sendDraftApi(
  draftId: string,
  payload: { subject?: string; body: string; visibility: 'requester_visible' | 'internal_only' }
): Promise<any> {
  const res = await apiClient.post(`/drafts/${draftId}/send`, payload);
  return res.data;
}
