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

        text = f"{title} {description}".lower()

        # 1. Category Classification
        if any(w in text for w in ["printer", "zebra", "thermal", "scanner", "barcode", "cnc", "plc", "kiosk", "touchscreen", "hardware", "monitor", "keyboard", "laptop", "cable", "dock", "sensor", "ram", "disk", "cpu", "motherboard", "overheat", "fan", "psu", "power supply", "bad sector"]):
            category = "Hardware"
            team = "Desktop & Field Support"
        elif any(w in text for w in ["network", "wifi", "vpn", "packet loss", "jitter", "latency", "dns", "subnet", "gateway", "router", "switch", "meraki", "cisco", "firewall", "bandwidth", "ethernet", "vlan", "ssid", "ping", "disconnect"]):
            category = "Network"
            team = "Network Engineering"
        elif any(w in text for w in ["password", "login", "account", "active directory", "ad", "ldap", "okta", "sso", "mfa", "2fa", "credentials", "permission", "role", "access denied", "locked", "unlock", "badge", "rfid"]):
            category = "Access & Identity"
            team = "Identity & Access"
        elif any(w in text for w in ["hvac", "power outage", "generator", "leak", "smoke", "air condition", "facilities", "building", "temperature"]):
            category = "Facilities & Ops"
            team = "Facilities & Infrastructure"
        else:
            category = "Software"
            team = "Enterprise Applications"

        # 2. Priority & Severity Classification
        if any(w in text for w in ["halted", "emergency", "outage", "stopped", "production down", "plant down", "line halted", "assembly halted", "critical", "cannot operate", "fatal", "blocking all", "disaster"]):
            priority = "P1"
            severity = "Critical"
        elif any(w in text for w in ["packet loss", "high latency", "jitter", "overheat", "degraded", "audit", "month end", "multiple users", "intermittent", "blocking", "urgent", "slow"]):
            priority = "P2"
            severity = "High"
        elif any(w in text for w in ["inquiry", "how to", "question", "request", "routine", "setup", "minor", "cosmetic", "info"]):
            priority = "P4"
            severity = "Low"
        else:
            priority = "P3"
            severity = "Medium"

        # 3. Dynamic Supporting Telemetry & Factors Extraction
        factors: List[str] = []

        # Error code detection
        import re
        error_matches = re.findall(r'(?:error|code|status|http|err|exception)[:\s\-]+([a-zA-Z0-9_\-]+)', text, re.IGNORECASE)
        if error_matches:
            factors.append(f"Detected Error/Telemetry Signature: '{error_matches[0].upper()}'")

        # Temperature / metric detection
        temp_match = re.search(r'(\d+)\s*(?:°c|celsius|degrees|%|ms|kb|mb|gb|ghz)', text, re.IGNORECASE)
        if temp_match:
            factors.append(f"Recorded Telemetry Metric: '{temp_match.group(0)}' in telemetry report")

        # Specific hardware/software keywords
        if "zebra" in text or "printer" in text:
            factors.append("Domain Match: Thermal/Industrial Printing & Barcode Dispatch Subsystem")
        elif "cnc" in text or "plc" in text or "robot" in text:
            factors.append("Domain Match: Automated Manufacturing & CNC Line Telemetry")
        elif "packet loss" in text or "jitter" in text or "vpn" in text or "wifi" in text:
            factors.append("Domain Match: Telemetry indicates WAN/WLAN transport layer degradation")
        elif "active directory" in text or "ldap" in text or "okta" in text or "password" in text:
            factors.append("Domain Match: Enterprise Identity Provider & Authentication Gateway")
        elif "postgres" in text or "sql" in text or "database" in text or "erp" in text or "sap" in text:
            factors.append("Domain Match: Relational Database & Core Enterprise Resource Planning (ERP)")
        else:
            factors.append(f"Domain Classification: '{category}' heuristic match based on reported symptoms")

        if priority == "P1":
            factors.append("Impact Assessment: Urgent operational disruption affecting active production/business workflow")
        elif priority == "P2":
            factors.append("Impact Assessment: High business impact with degraded service performance or compliance deadline")
        else:
            factors.append("Impact Assessment: Standard operational ticket within standard SLA turnaround")

        # 4. Contextual Missing Info Questions
        missing_info: List[str] = []
        if category == "Hardware":
            missing_info.append("What is the exact Device Asset Tag or Serial Number of the affected unit?")
            missing_info.append("Are status indicator LEDs solid green, flashing amber, or displaying a fault code?")
            missing_info.append("Has the unit and its immediate interface cable (USB/Ethernet) been power-cycled?")
        elif category == "Network":
            missing_info.append("Is the issue affecting wired Ethernet ports, wireless SSID, or VPN tunnels?")
            missing_info.append("Can you provide the output of 'ping' or 'traceroute' to your default gateway?")
            missing_info.append("Are adjacent workstations or the entire department subnet experiencing the drop?")
        elif category == "Access & Identity":
            missing_info.append("What is the requester's corporate Username / Employee ID?")
            missing_info.append("Is there an attached approval reference or Change Request (CR) number for this access?")
            missing_info.append("Is the account locked in Active Directory or failing SSO multi-factor authentication?")
        elif category == "Facilities & Ops":
            missing_info.append("Which building floor, wing, or server rack zone is affected?")
            missing_info.append("Have facility backup UPS/generators or emergency circuit breakers tripped?")
        else:
            missing_info.append("What exact software version or build number is currently installed?")
            missing_info.append("What are the exact step-by-step actions to reproduce the error or crash?")
            missing_info.append("Can you provide the application error log snippet or an attached screenshot?")

        if len(description.split()) < 8:
            missing_info.insert(0, "Can you provide additional context on what was being executed right before the failure?")

        return TriageResultDTO(
            suggested_category=category,
            suggested_severity=severity,
            suggested_priority=priority,
            confidence_score=0.92,
            supporting_factors=factors[:4],
            missing_info=missing_info[:3],
            suggested_team=team,
            recommended_next_action=f"Assign to {team} for immediate technical diagnosis.",
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
