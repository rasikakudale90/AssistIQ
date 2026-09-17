import { apiClient } from './client';
import { EscalationEvent, SLAInfo } from './types';

export async function getCaseSLAApi(caseId: string): Promise<SLAInfo> {
  const res = await apiClient.get<SLAInfo>(`/cases/${caseId}/sla`);
  return res.data;
}

export async function createManualEscalationApi(caseId: string, reason: string): Promise<EscalationEvent> {
  const res = await apiClient.post<EscalationEvent>(`/cases/${caseId}/escalate`, { reason });
  return res.data;
}

export async function listCaseEscalationsApi(caseId: string): Promise<EscalationEvent[]> {
  const res = await apiClient.get<EscalationEvent[]>(`/cases/${caseId}/escalations`);
  return res.data;
}

export async function acknowledgeEscalationApi(escalationId: string): Promise<EscalationEvent> {
  const res = await apiClient.post<EscalationEvent>(`/escalations/${escalationId}/acknowledge`);
  return res.data;
}

export async function runTheSweepApi(): Promise<any> {
  const res = await apiClient.post('/scheduler/sweep');
  return res.data;
}
