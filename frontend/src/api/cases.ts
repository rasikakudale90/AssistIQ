import { apiClient } from './client';
import { Case, CasePriority, CaseStatus, CaseType, AuditLog } from './types';

export interface CreateCasePayload {
  title: string;
  description: string;
  case_type?: CaseType;
  category?: string;
  priority?: CasePriority;
  site?: string;
}

export async function listCasesApi(params?: {
  status?: string;
  priority?: string;
  category?: string;
  assigned_operator_id?: string;
  assigned_team_id?: string;
  site?: string;
}): Promise<Case[]> {
  const res = await apiClient.get<Case[]>('/cases', { params });
  return res.data;
}

export async function getCaseApi(caseId: string): Promise<Case> {
  const res = await apiClient.get<Case>(`/cases/${caseId}`);
  return res.data;
}

export async function createCaseApi(payload: CreateCasePayload): Promise<Case> {
  const res = await apiClient.post<Case>('/cases', payload);
  return res.data;
}

export async function updateCaseStatusApi(caseId: string, status: CaseStatus, expectedVersion: number): Promise<Case> {
  const res = await apiClient.patch<Case>(`/cases/${caseId}/status`, {
    status,
    expected_version: expectedVersion,
  });
  return res.data;
}

export async function assignCaseApi(
  caseId: string,
  assignedOperatorId: string | null,
  assignedTeamId: string | null,
  expectedVersion: number
): Promise<Case> {
  const res = await apiClient.patch<Case>(`/cases/${caseId}/assign`, {
    assigned_operator_id: assignedOperatorId,
    assigned_team_id: assignedTeamId,
    expected_version: expectedVersion,
  });
  return res.data;
}

export async function updateCasePriorityApi(
  caseId: string,
  priority: CasePriority,
  expectedVersion: number
): Promise<Case> {
  const res = await apiClient.patch<Case>(`/cases/${caseId}/priority`, {
    priority,
    expected_version: expectedVersion,
  });
  return res.data;
}

export async function reopenCaseApi(caseId: string, reason: string): Promise<Case> {
  const res = await apiClient.post<Case>(`/cases/${caseId}/reopen`, { reason });
  return res.data;
}

export async function getCaseTimelineApi(caseId: string): Promise<AuditLog[]> {
  const res = await apiClient.get<AuditLog[]>(`/cases/${caseId}/timeline`);
  return res.data;
}

export async function getSimilarCasesApi(caseId: string): Promise<Array<{ id: string; reference_number: string; title: string; similarity_score: number }>> {
  const res = await apiClient.get(`/cases/${caseId}/similar`);
  return res.data;
}
