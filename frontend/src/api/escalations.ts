import { apiClient } from './client';
import { EscalationEvent, SLAInfo } from './types';

export async function getCaseSLAApi(caseId: string): Promise<SLAInfo> {
  const res = await apiClient.get<SLAInfo>(`/cases/${caseId}/sla`);
  return res.data;
}

export async function createManualEscalationApi(caseId: string, notes: string): Promise<EscalationEvent> {
  const res = await apiClient.post<EscalationEvent>(`/cases/${caseId}/escalate`, {
    reason: 'operator_requested',
    notes,
  });
  return res.data;
}

export async function listCaseEscalationsApi(caseId: string): Promise<EscalationEvent[]> {
  const res = await apiClient.get<any>(`/cases/${caseId}/escalations`);
  const raw = Array.isArray(res.data) ? res.data : (res.data?.items || []);
  return raw.map((ev: any) => ({
    ...ev,
    trigger_type: ev.trigger_reason?.toUpperCase() || ev.trigger_type || 'MANUAL',
    reason: ev.notes || ev.reason || `Triggered by ${ev.trigger_reason || 'system'}`,
    notified_role: ev.escalated_to || 'TeamLead / Manager',
  }));
}

export async function acknowledgeEscalationApi(escalationId: string): Promise<EscalationEvent> {
  const res = await apiClient.post<EscalationEvent>(`/escalations/${escalationId}/acknowledge`, {
    status: 'acknowledged',
  });
  return res.data;
}

export async function runTheSweepApi(): Promise<any> {
  const res = await apiClient.post('/scheduler/sweep');
  return res.data;
}
