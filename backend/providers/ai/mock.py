import logging
from typing import Dict, List, Optional
from backend.providers.ai.base import AIProvider, TriageResultDTO

logger = logging.getLogger("assistiq.ai.mock")


class MockAIProvider(AIProvider):
    """
    Deterministic Mock AI Provider for testing and offline environments.
    """

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def analyze_triage(
        self,
        title: str,
        description: str,
        case_type: str,
        site: Optional[str] = None,
        service_id: Optional[str] = None,
    ) -> Optional[TriageResultDTO]:
        if self.should_fail:
            return None

        title_lower = title.lower()
        if "network" in title_lower or "wifi" in title_lower or "vpn" in title_lower:
            category = "Network"
            team = "Network Engineering"
            priority = "P2"
            severity = "High"
        elif "password" in title_lower or "login" in title_lower or "account" in title_lower:
            category = "Access & Identity"
            team = "Identity & Access"
            priority = "P3"
            severity = "Medium"
        elif "laptop" in title_lower or "keyboard" in title_lower or "monitor" in title_lower:
            category = "Hardware"
            team = "Desktop Support"
            priority = "P3"
            severity = "Medium"
        else:
            category = "Software"
            team = "Service Desk"
            priority = "P3"
            severity = "Low"

        missing_info = []
        if len(description.split()) < 5:
            missing_info.append("Can you provide more specific steps to reproduce the issue?")
            missing_info.append("What error message or code is being displayed?")

        return TriageResultDTO(
            suggested_category=category,
            suggested_severity=severity,
            suggested_priority=priority,
            confidence_score=0.85,
            supporting_factors=[
                f"Keyword matching for '{category}' domain in case title and description",
                "Heuristic classification based on reported symptoms",
            ],
            missing_info=missing_info,
            suggested_team=team,
            recommended_next_action=f"Assign to {team} and verify requester location.",
        )

    async def generate_summary(
        self,
        case_title: str,
        case_description: str,
        case_status: str,
        messages_history: List[Dict[str, str]],
    ) -> Optional[str]:
        if self.should_fail:
            return None

        msg_count = len(messages_history)
        return (
            f"**What was reported**: {case_title} - {case_description[:100]}...\n"
            f"**What happened since**: {msg_count} message(s) exchanged. Current status is {case_status}.\n"
            f"**What's confirmed**: Issue logged and under active evaluation.\n"
            f"**What remains unresolved**: Final verification and resolution sign-off."
        )

    async def generate_communication_draft(
        self,
        draft_type: str,
        case_title: str,
        case_description: str,
        messages_history: List[Dict[str, str]],
        custom_instructions: Optional[str] = None,
    ) -> Optional[str]:
        if self.should_fail:
            return None

        templates = {
            "info_request": (
                f"Hello,\n\nThank you for reaching out regarding '{case_title}'. "
                f"To help us resolve this swiftly, could you please provide additional details or screenshots?\n\nBest regards,\nIT Support"
            ),
            "progress_update": (
                f"Hello,\n\nWe are actively working on '{case_title}'. "
                f"Our team is currently investigating the root cause and we will update you shortly.\n\nBest regards,\nIT Support"
            ),
            "resolution": (
                f"Hello,\n\nWe have applied a fix for '{case_title}'. "
                f"Please test and let us know if everything is working as expected.\n\nBest regards,\nIT Support"
            ),
            "escalation_summary": (
                f"Escalation Request for '{case_title}':\n"
                f"Issue summary: {case_description[:150]}\n"
                f"Reason: Requires tier-2 engineering review.\n"
            ),
        }
        return templates.get(draft_type, f"Update regarding '{case_title}'.")
