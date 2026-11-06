from typing import Dict, Any, List
from agents.state import AgentState

def critic_node(state: AgentState) -> Dict[str, Any]:
    """
    Critic / Verifier Agent (Agent #5):
    Inspects the generated draft petition and validates every statutory citation
    against the ground-truth retrieved documents and knowledge graph paths.
    Enforces the self-correcting reflection loop and generates localized citizen responses.
    """
    draft = state.get("draft_petition", "")
    citations = state.get("citations", [])
    docs = state.get("retrieved_documents", [])
    graph_knowledge = state.get("graph_knowledge", [])
    lang = state.get("detected_language", "en")
    trace = state.get("agent_trace", [])
    retry_count = state.get("retry_count", 0)

    trace.append(f"[Critic Agent] Verifying {len(citations)} citations against statutory grounding in language '{lang}'...")

    # Build comprehensive ground-truth corpus from retrieved docs and graph paths
    combined_ground_truth = " ".join([d.get("text", "") for d in docs])
    for item in graph_knowledge:
        combined_ground_truth += f" {item.get('source', '')} {item.get('relation', '')} {item.get('target', '')}"

    ground_truth_lower = combined_ground_truth.lower()
    ungrounded_citations = []

    for cit in citations:
        cit_clean = cit.lower()
        sec_match = False
        for marker in ["section 34", "section 35", "section 47", "section 58", "section 2(9)", "section 38",
                       "section 84", "section 69", "section 6", "section 7", "section 8", "section 19", "section 20",
                       "pm-kisan", "ayushman", "legal services"]:
            if marker in cit_clean:
                if marker in ground_truth_lower:
                    sec_match = True
                    break
        
        if not sec_match:
            tokens = [t for t in cit.replace(",", "").replace(".", "").split() if len(t) > 3 and t.lower() not in ["protection", "statutory", "2019", "2005"]]
            matches = [t for t in tokens if t.lower() in ground_truth_lower]
            if len(matches) < 1:
                ungrounded_citations.append(cit)

    is_grounded = len(ungrounded_citations) == 0
    feedback = (
        "All citations successfully verified against statutory texts and knowledge graph."
        if is_grounded else
        f"Ungrounded citations detected: {ungrounded_citations}. Reflection required."
    )

    trace.append(f"[Critic Agent] Grounding Check: {'PASSED (Faithfulness verified)' if is_grounded else 'FAILED (Hallucination detected)'} | Iteration: {retry_count + 1}")

    forum = state.get("eligibility_status", {}).get("recommended_forum", "Appropriate Forum")
    timeline = state.get("eligibility_status", {}).get("statutory_timeline", "Prescribed by law")
    portal = state.get("eligibility_status", {}).get("filing_portal", "Official Portal")

    final_output = _format_localized_response(lang, citations, forum, portal, timeline, is_grounded, draft)

    return {
        "is_grounded": is_grounded,
        "critic_feedback": feedback,
        "retry_count": retry_count + 1,
        "final_response": final_output,
        "agent_trace": trace
    }

def _format_localized_response(lang: str, citations: List[str], forum: str, portal: str, timeline: str, is_grounded: bool, draft: str) -> str:
    cit_list = chr(10).join(['* `' + c + '`' for c in citations])
    status_verified = "✅ Verified Grounded (No Hallucinations)" if is_grounded else "⚠️ Verification Pending"

    # Marathi
    if lang == "mr":
        return f"""### ⚖️ सहायक कायदेशीर निवारण सारांश

**प्रमाणित वैधानिक कलमे:**
{cit_list}

**अधिकारक्षेत्र व मंच मार्गदर्शन:**
* **शिफारस केलेला मंच / आयोग:** {forum}
* **दाखल पद्धत व पोर्टल:** {portal}
* **वैधानिक कालावधी:** {timeline}
* **कायदेशीर प्रमाणीकरण:** {status_verified}

---
### 📝 तयार केलेला औपचारिक मसुदा
```
{draft}
```
"""
    # Hindi
    elif lang == "hi":
        return f"""### ⚖️ सहायक विधिक निवारण सारांश

**प्रमाणित विधिक धाराएं:**
{cit_list}

**अधिकार क्षेत्र एवं आयोग विवरण:**
* **अनुशंसित फोरम / आयोग:** {forum}
* **दाखिल माध्यम एवं पोर्टल:** {portal}
* **विधिक समय-सीमा:** {timeline}
* **विधिक प्रमाणीकरण स्थिति:** {status_verified}

---
### 📝 जनरेट किया गया औपचारिक प्रारूप
```
{draft}
```
"""
    # Bengali
    elif lang == "bn":
        return f"""### ⚖️ সহায়ক আইনি প্রতিকার সারসংক্ষেপ

**বিধিবদ্ধ আইনি ধারা:**
{cit_list}

**নির্দিষ্ট এখতিয়ার ও ফোরাম:**
* **প্রস্তাবিত ফোরাম / কমিশন:** {forum}
* **দাখিলের মাধ্যম ও পোর্টাল:** {portal}
* **আইনি সময়সীমা:** {timeline}
* **আইনি যাচায় স্থিতি:** {status_verified}

---
### 📝 তৈরি করা বিধিবদ্ধ আবেদনপত্র
```
{draft}
```
"""
    # Tamil
    elif lang == "ta":
        return f"""### ⚖️ சஹாயக் சட்ட நிவாரண சுருக்கம்

**சட்டப்பிரிவு குறிப்புகள்:**
{cit_list}

**அதிகார வரம்பு மற்றும் மன்ற வழிகாட்டுதல்:**
* **பரிந்துரைக்கப்பட்ட மன்றம்:** {forum}
* **தாக்கல் முறை:** {portal}
* **சட்டபூர்வ காலக்கெடு:** {timeline}
* **சட்டப்பூர்வ சரிபார்ப்பு நிலை:** {status_verified}

---
### 📝 உருவாக்கப்பட்ட முறைப்படியான மனு
```
{draft}
```
"""
    # Telugu
    elif lang == "te":
        return f"""### ⚖️ సహాయక్ చట్టపరమైన పరిష్కార సారాంశం

**చట్ట నిబంధనలు:**
{cit_list}

**అధికార పరిధి మరియు ఫోరమ్ వివరాలు:**
* **సిఫార్సు చేయబడిన ఫోరమ్:** {forum}
* **దాఖలు విధానం:** {portal}
* **సమయ పరిమితి:** {timeline}
* **చట్టబద్ధమైన ధృవీకరణ:** {status_verified}

---
### 📝 రూపొందించిన అధికారిక దరఖాస్తు
```
{draft}
```
"""
    # Kannada
    elif lang == "kn":
        return f"""### ⚖️ ಸಹಾಯಕ ಕಾನೂನು ಪರಿಹಾರ ಸಾರಾಂಶ

**ಶಾಸನಬದ್ಧ ಉಲ್ಲೇಖಗಳು:**
{cit_list}

**ಅಧಿಕಾರ ವ್ಯಾಪ್ತಿ ಮತ್ತು ವೇದಿಕೆ:**
* **ಶಿಫಾರಸು ಮಾಡಿದ ವೇದಿಕೆ:** {forum}
* **ದಾಖಲಾತಿ ವಿಧಾನ:** {portal}
* **ಶಾಸನಬದ್ಧ ಗಡುವು:** {timeline}
* **ಕಾನೂನು ಮಾನ್ಯತೆ:** {status_verified}

---
### 📝 ರಚಿಸಲಾದ ಕಾನೂನುಬದ್ಧ ಅರ್ಜಿ
```
{draft}
```
"""
    # Malayalam
    elif lang == "ml":
        return f"""### ⚖️ സഹായക് നിയമ പരിഹാര സംഗ്രഹം

**നിയമപരമായ വകുപ്പുകൾ:**
{cit_list}

**അധികാര പരിധിയും ഫോറവും:**
* **ശുപാർശ ചെയ്യുന്ന ഫോറം:** {forum}
* **സമർപ്പണ രീതി:** {portal}
* **സമയപരിധി:** {timeline}
* **നിയമപരമായ സ്ഥിരീകരണം:** {status_verified}

---
### 📝 തയ്യാറാക്കിയ ഔദ്യോഗിക അപേക്ഷ
```
{draft}
```
"""
    # Gujarati
    elif lang == "gu":
        return f"""### ⚖️ સહાયક કાનૂની નિવારણ સારાંશ

**કાનૂની જોગવાઈઓ:**
{cit_list}

**અધિકારક્ષેત્ર અને ફોરમ માર્ગદર્શન:**
* **ભલામણ કરેલ ફોરમ:** {forum}
* **દાખલ પદ્ધતિ:** {portal}
* **સમયમર્યાદા:** {timeline}
* **કાનૂની માન્યતા:** {status_verified}

---
### 📝 તૈયાર કરેલ ઔપચારિક અરજી
```
{draft}
```
"""
    # Punjabi
    elif lang == "pa":
        return f"""### ⚖️ ਸਹਾਇਕ ਕਾਨੂੰਨੀ ਨਿਪਟਾਰਾ ਸਾਰ

**ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ:**
{cit_list}

**ਅਧਿਕਾਰ ਖੇਤਰ ਅਤੇ ਫੋਰਮ:**
* **ਸਿਫਾਰਸ਼ ਕੀਤਾ ਫੋਰਮ:** {forum}
* **ਦਾਖ਼ਲ ਕਰਨ ਦਾ ਤਰੀਕਾ:** {portal}
* **ਕਾਨੂੰਨੀ ਸਮਾਂ-ਸੀਮਾ:** {timeline}
* **ਕਾਨੂੰਨੀ ਪੁਸ਼ਟੀ:** {status_verified}

---
### 📝 ਤਿਆਰ ਕੀਤੀ ਰਸਮੀ ਦਰਖ਼ਾਸਤ
```
{draft}
```
"""
    # Odia
    elif lang == "or":
        return f"""### ⚖️ ସହାୟକ ଆଇନଗତ ପ୍ରତିକାର ସାରାଂଶ

**ବିଧିବଦ୍ଧ ଧାରା ସମୂହ:**
{cit_list}

**ଅଧିକାର କ୍ଷେତ୍ର ଓ କର୍ତ୍ତୃପକ୍ଷ:**
* **ସୁପାରିଶ କରାଯାଇଥିବା ଫୋରମ୍:** {forum}
* **ଦାଖଲ ପଦ୍ଧତି:** {portal}
* **ଆଇନଗତ ସମୟସୀମା:** {timeline}
* **ଆଇନଗତ ପ୍ରମାଣୀକରଣ:** {status_verified}

---
### 📝 ପ୍ରସ୍ତୁତ ବିଧିବଦ୍ଧ ଦରଖାସ୍ତ
```
{draft}
```
"""
    # Assamese
    elif lang == "as":
        return f"""### ⚖️ সহায়ক আইনী প্ৰতিকাৰ সাৰাংশ

**আইনী ধাৰাসমূহ:**
{cit_list}

**নিৰ্দিষ্ট কৰ্তৃপক্ষ আৰু ন্যায়ালয়:**
* **প্ৰস্তাৱিত ফ’ৰাম:** {forum}
* **দাখিলৰ মাধ্যম:** {portal}
* **আইনী সময়সীমা:** {timeline}
* **আইনী প্ৰমাণীকৰণ:** {status_verified}

---
### 📝 প্ৰস্তুত কৰা আইনী আবেদন
```
{draft}
```
"""
    # Urdu
    elif lang == "ur":
        return f"""### ⚖️ معاون قانونی حل کا خلاصہ

**قانونی دفعات:**
{cit_list}

**متعلقہ دائرہ اختیار اور فورم:**
* **تجویز کردہ فورم:** {forum}
* **دائر کرنے کا طریقہ:** {portal}
* **قانونی مدت:** {timeline}
* **قانونی تصدیق:** {status_verified}

---
### 📝 تیار کردہ باضابطہ قانونی ڈرافٹ
```
{draft}
```
"""
    # English default
    else:
        return f"""### ⚖️ Sahayak Legal Redressal Summary

**Grounded Statutory Citations:**
{cit_list}

**Designated Jurisdiction & Authority:**
* **Recommended Forum:** {forum}
* **Official Filing Mode:** {portal}
* **Statutory Timelines:** {timeline}
* **Citation Grounding Status:** {status_verified}

---
### 📝 Generated Formal Legal Draft
```
{draft}
```
"""
