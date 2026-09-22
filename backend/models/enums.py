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

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in ["local", "password", "pwd", "email"]:
                return cls.PASSWORD
            if val_lower in ["google", "oauth", "oidc"]:
                return cls.GOOGLE
        return None


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    AWAY = "away"
    OFFLINE = "offline"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_lower = value.lower()
            for member in cls:
                if member.value == val_lower:
                    return member
        return None


class CaseType(str, enum.Enum):
    INCIDENT = "Incident"
    SERVICE_REQUEST = "Service Request"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_clean = value.replace(" ", "").replace("_", "").lower()
            if "incident" in val_clean:
                return cls.INCIDENT
            if "servicerequest" in val_clean or "request" in val_clean:
                return cls.SERVICE_REQUEST
        return None


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

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            mapping = {
                "critical": cls.P1,
                "high": cls.P2,
                "medium": cls.P3,
                "low": cls.P4,
                "p1": cls.P1,
                "p2": cls.P2,
                "p3": cls.P3,
                "p4": cls.P4,
            }
            return mapping.get(value.lower())
        return None


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
