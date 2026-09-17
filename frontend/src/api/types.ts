export type UserRole = 'Requester' | 'Operator' | 'TeamLead' | 'Manager' | 'Administrator';

export type CaseType = 'Incident' | 'ServiceRequest';

export type CasePriority = 'P1' | 'P2' | 'P3' | 'P4';

export type CaseStatus =
  | 'Draft'
  | 'New'
  | 'InAssessment'
  | 'Assigned'
  | 'AwaitingRequester'
  | 'AwaitingApproval'
  | 'Resolved'
  | 'Closed'
  | 'Cancelled'
  | 'Reopened';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  site?: string;
  team_id?: string;
  email_verified?: boolean;
  is_active?: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface SLAInfo {
  id: string;
  case_id: string;
  priority: CasePriority;
  response_deadline: string;
  resolve_deadline: string;
  first_response_at?: string;
  resolved_at?: string;
  response_breached: boolean;
  resolve_breached: boolean;
  is_response_approaching: boolean;
  is_resolve_approaching: boolean;
  minutes_to_response_deadline?: number;
  minutes_to_resolve_deadline?: number;
}

export interface Case {
  id: string;
  reference_number: string;
  title: string;
  description: string;
  case_type: CaseType;
  category: string;
  priority: CasePriority;
  status: CaseStatus;
  requester_id: string;
  requester_email?: string;
  assigned_operator_id?: string;
  assigned_team_id?: string;
  site?: string;
  version: number;
  created_at: string;
  updated_at: string;
  closed_at?: string;
  resolved_at?: string;
  sla?: SLAInfo;
}

export interface AITriageResult {
  id: string;
  case_id: string;
  predicted_category: string;
  predicted_priority: CasePriority;
  confidence_score: number;
  supporting_factors: string[];
  missing_info_questions: string[];
  suggested_team?: string;
  recommended_next_action?: string;
  created_at: string;
}

export interface CaseSummary {
  id: string;
  case_id: string;
  summary_text: string;
  what_was_reported: string;
  what_happened_since: string;
  what_is_confirmed: string;
  what_remains_unresolved: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: string;
  case_id: string;
  risk_level: 'Low' | 'Moderate' | 'High' | 'Critical';
  risk_score: number;
  risk_factors: string[];
  recommended_action: string;
  created_at: string;
}

export interface EscalationEvent {
  id: string;
  case_id: string;
  trigger_type: 'SLA_BREACH' | 'REPEATED_REOPENS' | 'RISK_THRESHOLD' | 'MANUAL_OPERATOR';
  reason: string;
  notified_role: string;
  acknowledged_by_id?: string;
  acknowledged_at?: string;
  created_at: string;
}

export interface CommunicationDraft {
  id: string;
  case_id: string;
  draft_type: 'info_request' | 'progress_update' | 'resolution' | 'escalation_summary';
  recipient_role: string;
  subject: string;
  body: string;
  status: 'DRAFT' | 'APPROVED' | 'SENT' | 'DISCARDED';
  created_at: string;
}

export interface Message {
  id: string;
  case_id: string;
  sender_id: string;
  sender_email?: string;
  sender_role?: string;
  visibility: 'requester_visible' | 'internal_only';
  body: string;
  ai_generated: boolean;
  created_at: string;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  case_id: string;
  message_id?: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  storage_path: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  case_id: string;
  actor_id?: string;
  actor_email?: string;
  action: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  created_at: string;
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  slug: string;
  category: string;
  content: string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  view_count: number;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  active_cases: number;
  unassigned_cases: number;
  breached_cases: number;
  critical_p1_cases: number;
  total_cases: number;
}

export interface OperationalInsights {
  time_window: '7d' | '30d' | '90d' | 'all';
  total_cases: number;
  resolved_cases: number;
  reopened_cases: number;
  breached_cases: number;
  reopen_rate_percent: number;
  avg_resolution_minutes: number;
  sla_compliance_rate_percent: number;
  response_compliance_rate_percent: number;
  resolve_compliance_rate_percent: number;
  volume_by_category: Record<string, number>;
  volume_by_priority: Record<string, number>;
  volume_by_status: Record<string, number>;
  volume_by_site: Record<string, number>;
  team_metrics: Array<{
    team_id: string;
    team_name: string;
    assigned_count: number;
    resolved_count: number;
    breach_count: number;
    avg_resolution_minutes: number;
  }>;
  ai_narrative?: string;
}
