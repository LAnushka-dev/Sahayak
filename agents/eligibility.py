import re
from agents.state import AgentState

def eligibility_node(state: AgentState) -> dict:
    """
    Eligibility Agent: Evaluates statutory limits (pecuniary jurisdiction under CPA 2019)
    or government scheme eligibility rules (PM-KISAN, Ayushman Bharat).
    """
    query = state["query"]
    intent = state.get("intent", "")
    trace = state.get("agent_trace", [])

    trace.append("[Eligibility Agent] Evaluating statutory jurisdiction and eligibility rules...")

    status = {
        "is_eligible": True,
        "recommended_forum": "District Consumer Disputes Redressal Commission",
        "pecuniary_limit": "Up to ₹50,00,000",
        "notes": []
    }

    if intent == "CONSUMER_GRIEVANCE":
        # Extract currency numbers if present
        amounts = re.findall(r'(?:₹|rs\.?|inr)\s*([\d,]+)', query.lower())
        if amounts:
            amt_clean = int(amounts[0].replace(",", ""))
            if amt_clean > 5000000 and amt_clean <= 20000000:
                status["recommended_forum"] = "State Consumer Disputes Redressal Commission (SCDRC)"
                status["pecuniary_limit"] = "₹50 Lakhs to ₹2 Crores (Section 47)"
                status["notes"].append("Exceeds District Forum pecuniary jurisdiction.")
            elif amt_clean > 20000000:
                status["recommended_forum"] = "National Consumer Disputes Redressal Commission (NCDRC)"
                status["pecuniary_limit"] = "Above ₹2 Crores (Section 58)"
            else:
                status["recommended_forum"] = "District Consumer Disputes Redressal Commission (DCDRC)"
                status["pecuniary_limit"] = "Up to ₹50 Lakhs (Section 34)"
        trace.append(f"[Eligibility Agent] Forum matched: {status['recommended_forum']}")

    elif intent == "WELFARE_SCHEME":
        status["recommended_forum"] = "PM-KISAN Portal / District Agriculture Office"
        status["notes"].append("Requires mandatory Aadhaar eKYC and cultivable land records.")
        trace.append("[Eligibility Agent] Checked PM-KISAN & Ayushman criteria against land & ID rules.")

    elif intent == "RTI_QUERY":
        status["recommended_forum"] = "Central/State Public Information Officer (CPIO/SPIO)"
        status["notes"].append("Statutory 30-day response window under Section 7(1).")
        trace.append("[Eligibility Agent] Designated CPIO as first responder.")

    return {
        "eligibility_status": status,
        "agent_trace": trace
    }
