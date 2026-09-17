import { apiClient } from './client';
import { DashboardStats, OperationalInsights } from './types';

export async function getDashboardStatsApi(): Promise<DashboardStats> {
  const res = await apiClient.get<DashboardStats>('/insights/dashboard');
  return res.data;
}

export async function getOperationalInsightsApi(
  window: '7d' | '30d' | '90d' | 'all' = '30d'
): Promise<OperationalInsights> {
  const res = await apiClient.get<OperationalInsights>('/insights', {
    params: { window },
  });
  return res.data;
}

export async function exportCasesCsvApi(): Promise<Blob> {
  const res = await apiClient.get('/reports/export/cases.csv', {
    responseType: 'blob',
  });
  return res.data;
}
