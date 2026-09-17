import { apiClient } from './client';
import { Case, CasePriority, CaseStatus, CaseType, AuditLog } from './types';

export interface CreateCasePayload {
  title: string;
  description: string;
  case_type?: CaseType;
  type?: CaseType;
  category?: string;
  service_id?: string;
  priority?: CasePriority;
  site?: string;
}

export async function listCasesApi(params?: {
  status?: string;
  priority?: string;
  category?: string;
  type?: string;
  case_type?: string;
  owner_id?: string;
  assigned_operator_id?: string;
  team_id?: string;
  assigned_team_id?: string;
  site?: string;
  search?: string;
}): Promise<Case[]> {
  const queryParams: any = {};
  if (params?.status) queryParams.status = params.status;
  if (params?.priority) queryParams.priority = params.priority;
  if (params?.type || params?.case_type) queryParams.type = params.type || params.case_type;
  if (params?.owner_id || params?.assigned_operator_id) queryParams.owner_id = params.owner_id || params.assigned_operator_id;
  if (params?.team_id || params?.assigned_team_id) queryParams.team_id = params.team_id || params.assigned_team_id;
  if (params?.site) queryParams.site = params.site;
  if (params?.search) queryParams.search = params.search;

  const res = await apiClient.get<any>('/cases', { params: queryParams });
  const rawList = Array.isArray(res.data) ? res.data : (res.data?.items || []);
  return rawList.map((item: any) => ({
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  }));
}

export async function getCaseApi(caseId: string): Promise<Case> {
  const res = await apiClient.get<any>(`/cases/${caseId}`);
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function createCaseApi(payload: CreateCasePayload): Promise<Case> {
  const body: any = {
    title: payload.title,
    description: payload.description,
    type: payload.type || payload.case_type || 'Incident',
    priority: payload.priority || 'P3',
    site: payload.site || 'Main Facility',
  };
  if (payload.service_id || payload.category) {
    body.service_id = payload.service_id || payload.category;
  }
  const res = await apiClient.post<any>('/cases', body);
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function updateCaseStatusApi(caseId: string, status: CaseStatus, expectedVersion: number): Promise<Case> {
  const res = await apiClient.patch<any>(`/cases/${caseId}/status`, {
    status,
    version: expectedVersion,
  });
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function assignCaseApi(
  caseId: string,
  assignedOperatorId: string | null,
  assignedTeamId: string | null,
  expectedVersion: number
): Promise<Case> {
  const res = await apiClient.patch<any>(`/cases/${caseId}/assign`, {
    owner_id: assignedOperatorId,
    team_id: assignedTeamId,
    version: expectedVersion,
  });
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function updateCasePriorityApi(
  caseId: string,
  priority: CasePriority,
  expectedVersion: number,
  reason: string = 'Priority adjustment from IT workbench'
): Promise<Case> {
  const res = await apiClient.patch<any>(`/cases/${caseId}/priority`, {
    priority,
    reason,
    version: expectedVersion,
  });
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function reopenCaseApi(caseId: string, reason: string, version: number = 1): Promise<Case> {
  const res = await apiClient.post<any>(`/cases/${caseId}/reopen`, {
    reason,
    version,
  });
  const item = res.data;
  return {
    ...item,
    case_type: item.case_type || item.type || 'Incident',
    category: item.category || item.service_id || 'General Support',
    assigned_operator_id: item.assigned_operator_id || item.owner_id,
    assigned_team_id: item.assigned_team_id || item.team_id,
  };
}

export async function getCaseTimelineApi(caseId: string): Promise<AuditLog[]> {
  const res = await apiClient.get<AuditLog[]>(`/cases/${caseId}/timeline`);
  return Array.isArray(res.data) ? res.data : [];
}

export async function getSimilarCasesApi(caseId: string): Promise<Array<{ id: string; reference_number: string; title: string; similarity_score: number }>> {
  const res = await apiClient.get<any>(`/cases/${caseId}/similar`);
  const candidates = res.data?.candidates || res.data || [];
  return candidates.map((c: any) => ({
    id: c.case_id || c.id,
    reference_number: c.reference_number,
    title: c.title,
    similarity_score: c.similarity_score ?? 0.8,
  }));
}
