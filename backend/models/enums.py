import enum


class UserRole(str, enum.Enum):
    REQUESTER = "Requester"
    OPERATOR = "Operator"
    TEAM_LEAD = "TeamLead"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class AuthProvider(str, enum.Enum):
    PASSWORD = "password"
    GOOGLE = "google"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    AWAY = "away"
    OFFLINE = "offline"


class CaseType(str, enum.Enum):
    INCIDENT = "Incident"
    SERVICE_REQUEST = "Service Request"


class CaseStatus(str, enum.Enum):
    DRAFT = "Draft"
    NEW = "New"
    IN_ASSESSMENT = "InAssessment"
    ASSIGNED = "Assigned"
    AWAITING_REQUESTER = "AwaitingRequester"
    AWAITING_APPROVAL = "AwaitingApproval"
    PENDING_EXTERNAL = "PendingExternal"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class Priority(str, enum.Enum):
    P1 = "P1"  # Critical (15 min response / 4 hr resolution)
    P2 = "P2"  # High (1 hr response / 8 hr resolution)
    P3 = "P3"  # Medium (4 hr response / 72 hr resolution)
    P4 = "P4"  # Low (24 hr response / 120 hr resolution)


class MessageVisibility(str, enum.Enum):
    REQUESTER_VISIBLE = "requester_visible"
    INTERNAL_ONLY = "internal_only"


class ConfidenceLevel(str, enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class EscalationReason(str, enum.Enum):
    APPROACHING_DEADLINE = "approaching_deadline"
    MISSED_DEADLINE = "missed_deadline"
    HIGH_RISK = "high_risk"
    REPEATED_REOPEN = "repeated_reopen"
    OPERATOR_REQUESTED = "operator_requested"


class EscalationStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class DraftType(str, enum.Enum):
    INFO_REQUEST = "info_request"
    PROGRESS_UPDATE = "progress_update"
    RESOLUTION = "resolution"
    ESCALATION_SUMMARY = "escalation_summary"


class DraftStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    DISCARDED = "discarded"


class ApprovalDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KnowledgeState(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CaseRelationshipType(str, enum.Enum):
    RELATED_TO = "related_to"
    DUPLICATE_OF = "duplicate_of"
    PART_OF_MAJOR_INCIDENT = "part_of_major_incident"
