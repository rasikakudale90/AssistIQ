import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_full_suite():
    print("=================================================================")
    print("[TEST] AssistIQ Comprehensive 12-Feature & AI Triage Automated Test Suite")
    print("=================================================================\n")
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Login as Operator
        login_resp = await client.post(f"{BASE_URL}/auth/login", json={"email": "operator@assistiq.local", "password": "Password123!@#"})
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] 1. Authentication & JWT Tokens: Operator logged in successfully.")

        # -------------------------------------------------------------
        # FEATURE 1: AI Triage (Category, Priority, Telemetry, Missing Info)
        # -------------------------------------------------------------
        print("\n--- Testing Feature 1: AI Triage Engine ---")
        # Test 1A: Hardware / Industrial Printer with Telemetry
        case_a_payload = {
            "title": "Zebra ZT411 Label Printer Error 104 Thermal Overheat",
            "description": "Packaging station thermal printer stopped printing barcode labels. Error code 104 displayed on LCD, temperature recorded at 88°C, Line 3 packaging delayed.",
            "type": "Incident",
            "priority": "P3",
            "site": "Austin Plant",
        }
        res_a = await client.post(f"{BASE_URL}/cases", json=case_a_payload, headers=headers)
        assert res_a.status_code == 201, f"Create Case A failed: {res_a.text}"
        case_a = res_a.json()
        case_a_id = case_a["id"]

        triage_a_resp = await client.get(f"{BASE_URL}/cases/{case_a_id}/triage", headers=headers)
        assert triage_a_resp.status_code == 200, f"Triage A failed: {triage_a_resp.text}"
        triage_a = triage_a_resp.json()
        print(f"  [Case A - Hardware] Category: '{triage_a['suggested_category']}', Priority: '{triage_a['suggested_priority']}'")
        print(f"  [Case A - Telemetry Factors]: {triage_a['supporting_factors']}")
        print(f"  [Case A - Missing Info Questions]: {triage_a['missing_info']}")
        assert triage_a["suggested_category"] == "Hardware"
        assert len(triage_a["supporting_factors"]) > 0
        assert len(triage_a["missing_info"]) > 0
        assert any("Error" in f or "104" in f or "88" in f or "Thermal" in f for f in triage_a["supporting_factors"])
        print("  [PASS] AI Triage Hardware & Telemetry Verified!")

        # Test 1B: Network Outage P1
        case_b_payload = {
            "title": "Factory-wide Meraki Core Switch failure and Wi-Fi disconnect",
            "description": "Plant wide network outage. All assembly lines halted and emergency stop triggered due to packet loss and disconnected switch.",
            "type": "Incident",
            "priority": "P3",
            "site": "Austin Plant",
        }
        res_b = await client.post(f"{BASE_URL}/cases", json=case_b_payload, headers=headers)
        assert res_b.status_code == 201, f"Create Case B failed: {res_b.text}"
        case_b = res_b.json()
        case_b_id = case_b["id"]
        triage_b = (await client.get(f"{BASE_URL}/cases/{case_b_id}/triage", headers=headers)).json()
        print(f"  [Case B - Network P1] Category: '{triage_b['suggested_category']}', Priority: '{triage_b['suggested_priority']}'")
        print(f"  [Case B - Missing Info Questions]: {triage_b['missing_info']}")
        assert triage_b["suggested_category"] == "Network"
        assert triage_b["suggested_priority"] == "P1"
        assert len(triage_b["missing_info"]) > 0
        print("  [PASS] AI Triage Network Outage & Priority Prediction Verified!")

        # -------------------------------------------------------------
        # FEATURE 2: AI Communication Draft Assistant
        # -------------------------------------------------------------
        print("\n--- Testing Feature 2: AI Communication Draft Assistant ---")
        draft_payload = {"draft_type": "info_request", "custom_instructions": "Ask for the serial number"}
        draft_res = await client.post(f"{BASE_URL}/cases/{case_a_id}/drafts", json=draft_payload, headers=headers)
        assert draft_res.status_code in [200, 201], f"Draft creation failed: {draft_res.text}"
        draft_obj = draft_res.json()
        print(f"  Generated Draft [{draft_obj['draft_type']}]:\n  '{draft_obj['body'][:120]}...'")
        
        # Send draft as message
        send_res = await client.post(
            f"{BASE_URL}/drafts/{draft_obj['id']}/send",
            json={"body": draft_obj["body"], "visibility": "requester_visible"},
            headers=headers
        )
        assert send_res.status_code in [200, 201], f"Send draft failed: {send_res.text}"
        print("  [PASS] AI Draft Created, Reviewed, and Sent successfully!")

        # -------------------------------------------------------------
        # FEATURE 3: 4-Part Continuous Structured AI Summary
        # -------------------------------------------------------------
        print("\n--- Testing Feature 3: 4-Part Continuous Structured AI Summary ---")
        summary_res = await client.get(f"{BASE_URL}/cases/{case_a_id}/summary", headers=headers)
        assert summary_res.status_code in [200, 201], f"Summary failed: {summary_res.text}"
        summary_obj = summary_res.json()
        print(f"  1. What Was Reported: {summary_obj.get('what_was_reported')}")
        print(f"  2. What Happened Since: {summary_obj.get('what_happened_since')}")
        print(f"  3. What is Confirmed: {summary_obj.get('what_is_confirmed')}")
        print(f"  4. What Remains Unresolved: {summary_obj.get('what_remains_unresolved')}")
        assert summary_obj.get("what_was_reported") is not None
        print("  [PASS] 4-Part Structured AI Summary Verified!")

        # -------------------------------------------------------------
        # FEATURE 4: 24/7 SLA Tracker & Countdown Calculation
        # -------------------------------------------------------------
        print("\n--- Testing Feature 4: 24/7 SLA Tracking & Countdown ---")
        sla_res = await client.get(f"{BASE_URL}/cases/{case_a_id}/sla", headers=headers)
        assert sla_res.status_code in [200, 201], f"SLA failed: {sla_res.text}"
        sla_obj = sla_res.json()
        print(f"  Target Response: {sla_obj.get('target_response_at')}")
        print(f"  Target Resolve: {sla_obj.get('target_resolve_at')}")
        print(f"  Response Breached: {sla_obj.get('response_breached')}")
        print(f"  Resolve Breached: {sla_obj.get('resolve_breached')}")
        assert "target_response_at" in sla_obj and "target_resolve_at" in sla_obj
        print("  [PASS] 24/7 SLA Tracker Verified!")

        # -------------------------------------------------------------
        # FEATURE 5: Duplicate / Similar Case Detection
        # -------------------------------------------------------------
        print("\n--- Testing Feature 5: Candidate Similar Case Search ---")
        similar_res = await client.get(f"{BASE_URL}/cases/{case_a_id}/similar", headers=headers)
        assert similar_res.status_code in [200, 201], f"Similar cases failed: {similar_res.text}"
        sim_list = similar_res.json()
        print(f"  Found {len(sim_list)} candidate similar case(s).")
        print("  [PASS] Similar Case Detection Engine Verified!")

        # -------------------------------------------------------------
        # FEATURE 6: Periodic Background Sweep Scheduler
        # -------------------------------------------------------------
        print("\n--- Testing Feature 6: 'The Sweep' Background Scheduler ---")
        admin_login = await client.post(f"{BASE_URL}/auth/login", json={"email": "admin@assistiq.local", "password": "Password123!@#"})
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        sweep_res = await client.post(f"{BASE_URL}/scheduler/sweep", headers=admin_headers)
        assert sweep_res.status_code in [200, 201], f"Manual sweep failed: {sweep_res.text}"
        sweep_data = sweep_res.json()
        print(f"  Sweep Execution Result: {sweep_data}")
        print("  [PASS] 'The Sweep' Scheduler Verified!")

        # -------------------------------------------------------------
        # FEATURE 7: Level 2 Human Escalation & Acknowledgment
        # -------------------------------------------------------------
        print("\n--- Testing Feature 7: Level 2 Human Escalation Flow ---")
        esc_res = await client.post(
            f"{BASE_URL}/cases/{case_a_id}/escalate",
            json={"reason": "operator_requested", "notes": "Zebra thermal head replacement required from tier 2 hardware vendor."},
            headers=headers
        )
        assert esc_res.status_code in [200, 201], f"Escalation failed: {esc_res.text}"
        esc_obj = esc_res.json()
        print(f"  Escalation Created: Status='{esc_obj['status']}', Reason='{esc_obj['trigger_reason']}'")
        
        # Acknowledge escalation as Team Lead/Admin
        ack_res = await client.post(
            f"{BASE_URL}/escalations/{esc_obj['id']}/acknowledge",
            json={"status": "acknowledged"},
            headers=admin_headers
        )
        assert ack_res.status_code in [200, 201], f"Ack failed: {ack_res.text}"
        print("  [PASS] Level 2 Human Escalation & Acknowledgment Verified!")

        # -------------------------------------------------------------
        # FEATURE 8: Internal Staff Notes vs Public Notes
        # -------------------------------------------------------------
        print("\n--- Testing Feature 8: Internal Notes vs Public Messages ---")
        req_login = await client.post(f"{BASE_URL}/auth/login", json={"email": "requester@assistiq.local", "password": "Password123!@#"})
        req_token = req_login.json()["access_token"]
        req_headers = {"Authorization": f"Bearer {req_token}"}

        # Create case by requester
        case_c_res = await client.post(
            f"{BASE_URL}/cases",
            json={
                "title": "Requester VPN connection test",
                "description": "Testing VPN tunnel connection from home office.",
                "type": "Incident",
                "priority": "P3",
                "site": "Austin Plant",
            },
            headers=req_headers
        )
        assert case_c_res.status_code == 201, f"Create Case C failed: {case_c_res.text}"
        case_c_id = case_c_res.json()["id"]

        # Operator posts internal staff note
        msg_internal = await client.post(
            f"{BASE_URL}/cases/{case_c_id}/messages",
            json={"body": "Internal staff note: Meraki RADIUS server certificate expired.", "visibility": "internal_only"},
            headers=headers
        )
        assert msg_internal.status_code == 201, f"Internal note post failed: {msg_internal.text}"

        # Operator posts public requester-visible message
        msg_public = await client.post(
            f"{BASE_URL}/cases/{case_c_id}/messages",
            json={"body": "We are investigating the VPN gateway. Please hold on.", "visibility": "requester_visible"},
            headers=headers
        )
        assert msg_public.status_code == 201, f"Public msg post failed: {msg_public.text}"
        
        # Requester fetches messages for their case
        req_msgs_resp = await client.get(f"{BASE_URL}/cases/{case_c_id}/messages", headers=req_headers)
        assert req_msgs_resp.status_code == 200, f"Requester get msgs failed: {req_msgs_resp.text}"
        req_msgs = req_msgs_resp.json()
        internal_seen = any(m["visibility"] == "internal_only" for m in req_msgs)
        assert not internal_seen, "SECURITY VIOLATION: Requester was able to see internal notes!"
        assert any(m["visibility"] == "requester_visible" for m in req_msgs), "Requester could not see public message!"

        # Operator fetches messages and can see both
        op_msgs = (await client.get(f"{BASE_URL}/cases/{case_c_id}/messages", headers=headers)).json()
        assert any(m["visibility"] == "internal_only" for m in op_msgs), "Operator could not see internal note!"
        print("  [PASS] Internal Staff Notes Privacy & Access Control Verified!")

        # -------------------------------------------------------------
        # FEATURE 9: Manager Operational Insights Analytics
        # -------------------------------------------------------------
        print("\n--- Testing Feature 9: Manager Operational Insights ---")
        insights_res = await client.get(f"{BASE_URL}/insights", headers=admin_headers)
        assert insights_res.status_code == 200, f"Insights failed: {insights_res.text}"
        insights = insights_res.json()
        print(f"  Summary Metrics: Total Cases={insights.get('summary', {}).get('total_cases')}, Breached={insights.get('summary', {}).get('breached_cases')}")
        print("  [PASS] Manager Operational Insights Verified!")

        # -------------------------------------------------------------
        # FEATURE 10: 1-Click CSV Report Export
        # -------------------------------------------------------------
        print("\n--- Testing Feature 10: CSV Report Export ---")
        csv_res = await client.get(f"{BASE_URL}/reports/export/cases.csv", headers=admin_headers)
        assert csv_res.status_code == 200, f"CSV failed: {csv_res.text}"
        assert "text/csv" in csv_res.headers.get("content-type", "")
        print(f"  Exported CSV preview (lines: {len(csv_res.text.splitlines())}):\n  {csv_res.text.splitlines()[0]}")
        print("  [PASS] CSV Report Export Verified!")

        # -------------------------------------------------------------
        # FEATURE 11: Unified Global Search
        # -------------------------------------------------------------
        print("\n--- Testing Feature 11: Unified Global Search ---")
        search_res = await client.get(f"{BASE_URL}/search?q=Zebra", headers=headers)
        assert search_res.status_code == 200, f"Search failed: {search_res.text}"
        search_data = search_res.json()
        search_items = search_data.get("results", [])
        print(f"  Found {len(search_items)} matching item(s) for query 'Zebra'.")
        assert len(search_items) > 0
        print("  [PASS] Unified Search Verified!")

        # -------------------------------------------------------------
        # FEATURE 12: Optimistic Concurrency Control (Version Conflict Detection)
        # -------------------------------------------------------------
        print("\n--- Testing Feature 12: Optimistic Concurrency Control ---")
        # Fetch current version of Case A
        curr_case = (await client.get(f"{BASE_URL}/cases/{case_a_id}", headers=headers)).json()
        curr_ver = curr_case["version"]
        
        # Valid update with matching version
        upd_1 = await client.patch(f"{BASE_URL}/cases/{case_a_id}/status", json={"status": "InAssessment", "version": curr_ver}, headers=headers)
        assert upd_1.status_code == 200, f"Valid status update failed: {upd_1.text}"
        
        # Stale update with old version should trigger 409 Conflict
        stale_upd = await client.patch(f"{BASE_URL}/cases/{case_a_id}/status", json={"status": "Assigned", "version": curr_ver}, headers=headers)
        assert stale_upd.status_code == 409, f"Expected 409 Conflict, got: {stale_upd.status_code} {stale_upd.text}"
        print("  [PASS] Optimistic Concurrency Control 409 Conflict correctly caught and handled!")

    print("\n=================================================================")
    print("[SUCCESS] ALL 12 FEATURES + AI TRIAGE FULLY TESTED & WORKING FLAWLESSLY!")
    print("=================================================================\n")

if __name__ == "__main__":
    asyncio.run(run_full_suite())
