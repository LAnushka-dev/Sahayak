import re
from typing import List, Dict, Any
from agents.state import AgentState

def drafter_node(state: AgentState) -> Dict[str, Any]:
    """
    Drafter Agent (Agent #4):
    Synthesizes retrieved statutory text, knowledge graph paths, and citizen grievance
    to draft a formal legal petition, complaint, or application with grounded citations
    across 12 Indian languages + English:
    Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi, Odia, Assamese, Urdu, and English.
    Tailors the petition type dynamically:
    - Consumer Grievance -> Formal Consumer Complaint under Section 35
    - RTI Query -> Statutory Right to Information Application under Section 6 & 7(1)
    - Welfare Scheme -> Government Scheme Benefit Claim & Grievance Representation
    - General Inquiry -> Legal Aid Application under Legal Services Authorities Act
    """
    query = state["query"]
    intent = state.get("intent", "CONSUMER_GRIEVANCE")
    lang = state.get("detected_language", "en")
    docs = state.get("retrieved_documents", [])
    graph_knowledge = state.get("graph_knowledge", [])
    eligibility = state.get("eligibility_status", {})
    trace = state.get("agent_trace", [])

    trace.append(f"[Drafter Agent] Drafting formal petition for intent '{intent}' in language code: '{lang}'...")

    combined_context = " ".join([d.get("text", "") for d in docs])
    for g in graph_knowledge:
        combined_context += f" {str(g)}"

    citations = []

    # Dynamic statutory section extraction
    if intent == "CONSUMER_GRIEVANCE":
        forum = eligibility.get("recommended_forum", "")
        if "National" in forum or "NCDRC" in forum or "Section 58" in combined_context:
            citations.append("Consumer Protection Act 2019, Section 58")
        elif "State" in forum or "SCDRC" in forum or "Section 47" in combined_context:
            citations.append("Consumer Protection Act 2019, Section 47")
        else:
            citations.append("Consumer Protection Act 2019, Section 34")

        citations.append("Consumer Protection Act 2019, Section 35")

        if "2(9)" in combined_context or "right" in query.lower() or "हक्क" in query or "অধিকার" in query or "உரிமை" in query:
            citations.append("Consumer Protection Act 2019, Section 2(9)")
        if "84" in combined_context or "defect" in query.lower() or "खराब" in query or "नादुरुस्त" in query:
            citations.append("Consumer Protection Act 2019, Section 84")
        if "38" in combined_context:
            citations.append("Consumer Protection Act 2019, Section 38")

    elif intent == "RTI_QUERY":
        citations.append("Right to Information Act 2005, Section 6")
        citations.append("Right to Information Act 2005, Section 7(1)")
        if "appeal" in query.lower() or "अपील" in query or "আপিল" in query or "19" in combined_context:
            citations.append("Right to Information Act 2005, Section 19")
        if "penalty" in query.lower() or "दंड" in query or "20" in combined_context:
            citations.append("Right to Information Act 2005, Section 20")
        if "8" in combined_context or "exemption" in query.lower():
            citations.append("Right to Information Act 2005, Section 8")

    elif intent == "WELFARE_SCHEME":
        if "ayushman" in query.lower() or "आरोग्य" in query or "hospital" in query.lower() or "চিকিৎসা" in query or "சிகிச்சை" in query:
            citations.append("Ayushman Bharat PM-JAY Operational Guidelines")
        else:
            citations.append("PM-KISAN Operational Guidelines 2019")
    else:
        citations.append("National Legal Services Authorities Act, 1987")

    # Deduplicate citations while preserving order
    unique_citations = []
    for c in citations:
        if c not in unique_citations:
            unique_citations.append(c)

    forum_name = eligibility.get("recommended_forum", "Appropriate Statutory Forum")
    cit_text = "; ".join(unique_citations)
    timeline = eligibility.get("statutory_timeline", "As prescribed by law")
    portal = eligibility.get("filing_portal", "Official Portal / Offline Commission")

    draft = _generate_multilingual_draft(lang, intent, query, forum_name, cit_text, portal, timeline, unique_citations, eligibility)

    trace.append(f"[Drafter Agent] Draft completed in language '{lang}' with {len(unique_citations)} statutory citations.")

    return {
        "draft_petition": draft.strip(),
        "citations": unique_citations,
        "agent_trace": trace
    }

def _generate_multilingual_draft(lang: str, intent: str, query: str, forum: str, cit_text: str, portal: str, timeline: str, citations: List[str], eligibility: Dict[str, Any] = None) -> str:
    """
    Renders intent-tailored formal drafts in 12 Indian languages + English.
    """
    eligibility = eligibility or {}
    # -------------------------------------------------------------
    # 1. MARATHI (मराठी)
    # -------------------------------------------------------------
    if lang == "mr":
        if intent == "RTI_QUERY":
            return f"""माहितीचा अधिकार अधिनियम २००५ अंतर्गत अर्ज (कलम ६)
सादर: जन माहिती अधिकारी / {forum}

विषय: {query} बाबत माहिती मिळणेबाबत.

महोदय / महोदया,
१. अर्जदार माहितीचा अधिकार कायदा २००५ च्या कलम ६(१) अन्वये खालील माहितीची मागणी करत आहे:
   वैधानिक संदर्भ: {cit_text}
   विहित मुदत: कलम ७(१) नुसार ३० दिवसांच्या आत माहिती पुरवणे बंधनकारक आहे.

२. मागवलेल्या माहितीचा तपशील:
   "{query}"

३. अर्जाचे शुल्क: विहित शुल्क (रु. १०) ई-पेमेंट / डिमांड ड्राफ्ट / कोर्ट फी स्टॅम्पद्वारे जोडले आहे.
   दाखल पोर्टल: {portal}

आपला नम्र,
[अर्जदाराचे नाव / स्वाक्षरी]"""
        elif intent == "WELFARE_SCHEME":
            return f"""शासकीय जनकल्याण योजना लाभ व निवारण अर्ज
सादर: सक्षम प्राधिकारी / {forum}

विषय: {query} योजनेच्या लाभाबाबत अधिकृत अर्ज.

महोदय,
१. अर्जदार खालील मार्गदर्शक तत्त्वांच्या अधीन राहून लाभाची मागणी करत आहे:
   वैधानिक संदर्भ: {cit_text}
   वितरण पद्धत: थेट लाभ हस्तांतरण (DBT) आधार संलग्न बँक खात्यात

२. अर्जाचा तपशील व वस्तुस्थिती:
   "{query}"

३. पात्रता पूर्तता: शेतजमीन महसूल नोंद / आधार ई-केवायसी पूर्तता केली आहे.
   पोर्टल: {portal}

आपला नम्र,
[अर्जदाराचे नाव / स्वाक्षरी]"""
        else:
            return f"""औपचारिक कायदेशीर तक्रार / अर्ज (मसुदा)
सादर: मा. {forum}

विषय: {query} बाबत वैधानिक दाद मिळणेबाबत.

महोदय / महोदया,
१. अर्जदार खालील अधिकृत कायदेशीर कलमांनुसार ही तक्रार दाखल करत आहे:
   वैधानिक संदर्भ: {cit_text}
   दाखल पोर्टल: {portal} | वैधानिक कालावधी: {timeline}

२. तक्रारीचा तपशील:
   "{query}"

३. प्रार्थना / मागणी:
   अ. सदर प्रकरणाची तात्काळ दखल घेऊन योग्य आदेश पारित करावेत.
   ब. झालेल्या आर्थिक व मानसिक त्रासाबद्दल योग्य नुकसानभरपाई मंजूर करावी.

आपला नम्र,
[अर्जदाराचे नाव / स्वाक्षरी]"""

    # -------------------------------------------------------------
    # 2. HINDI (हिंदी)
    # -------------------------------------------------------------
    elif lang == "hi":
        if intent == "RTI_QUERY":
            return f"""सूचना का अधिकार अधिनियम, 2005 के अंतर्गत आवेदन (धारा 6)
समक्ष: लोक सूचना अधिकारी (CPIO/SPIO) / {forum}

विषय: {query} के संदर्भ में विधिक सूचना प्राप्ति हेतु आवेदन।

महोदय / महोदया,
१. प्रार्थी सूचना का अधिकार अधिनियम, 2005 की धारा 6 के तहत निम्नलिखित सूचना की मांग करता है:
   विधिक संदर्भ: {cit_text}
   विधिक समय-सीमा: धारा 7(1) के तहत 30 दिवस के भीतर (जीवन-स्वतंत्रता मामले में 48 घंटे)

२. वांछित सूचना का विवरण:
   "{query}"

३. आवेदन शुल्क: नियमानुसार ₹10 का शुल्क संलग्न है।
   दाखिल पोर्टल: {portal}

भवदीय,
[प्रार्थी का नाम / हस्ताक्षर]"""
        elif intent == "WELFARE_SCHEME":
            return f"""केंद्रीय जनकल्याण योजना लाभ एवं निवारण आवेदन
समक्ष: सक्षम प्राधिकारी / {forum}

विषय: {query} के अंतर्गत देय लाभ जारी करने हेतु आवेदन।

महोदय,
१. प्रार्थी निम्नलिखित आधिकारिक दिशा-निर्देशों के अंतर्गत आवेदन प्रस्तुत कर रहा है:
   विधिक संदर्भ: {cit_text}
   पोर्टल: {portal}

२. वस्तुस्थिति एवं विवरण:
   "{query}"

३. प्रार्थना: प्रार्थी की पात्रता का सत्यापन कर यथाशीघ्र देय लाभ डीबीटी के माध्यम से बैंक खाते में अंतरित किया जाए।

भवदीय,
[प्रार्थी का नाम / हस्ताक्षर]"""
        else:
            return f"""औपचारिक विधिक शिकायत / आवेदन (प्रारूप)
समक्ष: माननीय {forum}

विषय: {query} के संदर्भ में विधिक उपचार एवं निवारण हेतु।

महोदय / महोदया,
१. प्रार्थी निम्नलिखित विधिक धाराओं के अंतर्गत शिकायत प्रस्तुत कर रहा है:
   विधिक संदर्भ: {cit_text}
   दाखिल पोर्टल: {portal} | समय-सीमा: {timeline}

२. शिकायत का विवरण:
   "{query}"

३. प्रार्थना:
   क. मामले का त्वरित संज्ञान लेकर विपक्षी को उचित निर्देश दिए जाएं।
   ख. प्रार्थी को हुई आर्थिक व मानसिक क्षति हेतु उचित हर्जाना प्रदान किया जाए।

भवदीय,
[प्रार्थी का नाम / हस्ताक्षर]"""

    # -------------------------------------------------------------
    # 3. BENGALI (বাংলা)
    # -------------------------------------------------------------
    elif lang == "bn":
        if intent == "RTI_QUERY":
            return f"""তথ্য অধিকার আইন, ২০০৫ অনুযায়ী আবেদনপত্র (ধারা ৬)
প্রতি: জন তথ্য আধিকারিক (CPIO/SPIO) / {forum}

বিষয়: {query} সংক্রান্ত তথ্য পাওয়ার আবেদন।

মহাশয় / মহাশয়া,
১. আবেদনকারী তথ্য অধিকার আইনের ধারা ৬ অনুযায়ী নিম্নবর্ণিত তথ্য প্রার্থনা করছেন:
   আইনি সূত্র: {cit_text}
   নিষ্পত্তির সময়সীমা: ধারা ৭(১) অনুযায়ী ৩০ কার্যদিবস

২. প্রার্থিত তথ্যের বিবরণ:
   "{query}"

৩. আবেদন ফি: নিয়মমাফিক ১০ টাকার ফি সংযোজিত। পোর্টাল: {portal}

বিনীত,
[আবেদনকারীর নাম / স্বাক্ষর]"""
        elif intent == "WELFARE_SCHEME":
            return f"""সরকারি জনকল্যাণমূলক প্রকল্প সাহায্য ও প্রতিকার আবেদন
প্রতি: উপযুক্ত কর্তৃপক্ষ / {forum}

বিষয়: {query} সংক্রান্ত সুযোগ-সুবিধা পাওয়ার আবেদনপত্র।

মহাশয়,
১. আবেদনকারী নিম্নলিখিত বিধিবদ্ধ নির্দেশিকা অনুযায়ী আবেদন পেশ করছেন:
   আইনি সূত্র: {cit_text} | পোর্টাল: {portal}

২. অভিযোগ ও বাস্তব পরিস্থিতি:
   "{query}"

৩. প্রার্থনা: আবেদনকারীর যোগ্যতা যাচাই করে অবিলম্বে ডিবিটি মাধ্যমে আর্থিক সহায়তা প্রদান করা হোক।

বিনীত,
[আবেদনকারীর নাম / স্বাক্ষর]"""
        else:
            return f"""বিধিবদ্ধ আইনি অভিযোগ / আবেদনপত্র (খসড়া)
প্রতি: মাননীয় {forum}

বিষয়: {query} সংক্রান্ত বিষয়ে আইনি প্রতিকার প্রার্থনা।

মহাশয় / মহাশয়া,
১. আবেদনকারী নিম্নলিখিত বিধিবদ্ধ ধারাসমূহের অধীনে এই অভিযোগ দাখিল করছেন:
   আইনি সূত্র: {cit_text}
   দাখিলের পোর্টাল: {portal} | আইনি সময়সীমা: {timeline}

২. অভিযোগের বিবরণ:
   "{query}"

৩. প্রার্থনা: অবিলম্বে ন্যায়সঙ্গত প্রতিকার ও মানসিক-আর্থিক ক্ষতির উপযুক্ত ক্ষতিপূরণ মঞ্জুর করা হোক।

বিনীত,
[আবেদনকারীর নাম / স্বাক্ষর]"""

    # -------------------------------------------------------------
    # 4. TAMIL (தமிழ்)
    # -------------------------------------------------------------
    elif lang == "ta":
        if intent == "RTI_QUERY":
            return f"""தகவல் அறியும் உரிமைச் சட்டம் 2005 இன் கீழ் விண்ணப்பம் (பிரிவு 6)
முன்னிலை: பொது தகவல் அதிகாரி (CPIO/SPIO) / {forum}

பொருள்: {query} தொடர்பான தகவல்களைப் பெறுதல்.

ஐயா / அம்மா,
1. மனுதாரர் தகவல் அறியும் உரிமைச் சட்டம் பிரிவு 6 இன் கீழ் கீழ்வரும் தகவல்களைக் கோருகிறார்:
   சட்ட குறிப்புகள்: {cit_text}
   பதில் அளிக்கும் காலக்கெடு: பிரிவு 7(1) இன் கீழ் 30 நாட்கள்

2. கோரப்படும் தகவலின் விவரம்:
   "{query}"

3. கட்டணம்: அரசு விதிகளின்படி ₹10 கட்டணம் செலுத்தப்பட்டுள்ளது. தாக்கல் தளம்: {portal}

இப்படிக்கு,
[மனுதாரர் பெயர் / கையொப்பம்]"""
        elif intent == "WELFARE_SCHEME":
            return f"""அரசு நலத்திட்ட உதவி கோரும் மனு
முன்னிலை: தகுதிவாய்ந்த அதிகாரி / {forum}

பொருள்: {query} திட்டத்தின் பலன்களைப் பெறுதல் தொடர்பான கோரிக்கை.

ஐயா,
1. மனுதாரர் கீழ்வரும் அரசு வழிகாட்டுதல்களின்படி நிவாரணம் கோருகிறார்:
   சட்ட குறிப்புகள்: {cit_text} | தளம்: {portal}

2. உண்மை நிலை மற்றும் விவரங்கள்:
   "{query}"

3. கோரிக்கை: தகுதியைச் சரிபார்த்து வங்கிக் கணக்கில் நேரடியாகத் தொகையை வழங்க வேண்டுகிறேன்.

இப்படிக்கு,
[மனுதாரர் பெயர் / கையொப்பம்]"""
        else:
            return f"""முறைப்படியான சட்டபூர்வ புகார் மனு (வரைவு)
முன்னிலை: மதிப்பிற்குரிய {forum}

பொருள்: {query} தொடர்பான சட்டபூர்வ நிவாரணம் கோருதல்.

ஐயா / அம்மா,
1. மனுதாரர் பின்வரும் சட்டப் பிரிவுகளின் கீழ் இந்த முறைப்படியான புகாரை சமர்ப்பிக்கிறார்:
   சட்ட குறிப்புகள்: {cit_text}
   தாக்கல் தளம்: {portal} | சட்டபூர்வ காலக்கெடு: {timeline}

2. புகாரின் விவரம்:
   "{query}"

3. கோரிக்கை: தகுந்த இழப்பீடு மற்றும் உடனடி தீர்வை வழங்குமாறு வேண்டுகிறேன்.

இப்படிக்கு,
[மனுதாரர் பெயர் / கையொப்பம்]"""

    # -------------------------------------------------------------
    # 5. TELUGU (తెలుగు)
    # -------------------------------------------------------------
    elif lang == "te":
        if intent == "RTI_QUERY":
            return f"""సమాచార హక్కు చట్టం 2005 క్రింద దరఖాస్తు (సెక్షన్ 6)
సమక్షం: పౌర సమాచార అధికారి (CPIO/SPIO) / {forum}

విషయం: {query} కు సంబంధించిన సమాచారం కోరుతూ దరఖాస్తు.

అయ్యా / అమ్మా,
1. దరఖాస్తుదారు సమాచార హక్కు చట్టం సెక్షన్ 6 ప్రకారం క్రింది సమాచారాన్ని కోరుతున్నారు:
   చట్ట నిబంధనలు: {cit_text}
   పరిష్కార గడువు: సెక్షన్ 7(1) ప్రకారం 30 రోజులు

2. కోరబడిన సమాచారం వివరాలు:
   "{query}"

3. ఫీజు: నిబంధనల ప్రకారం ₹10 ఫీజు చెల్లించడమైనది. పోర్టల్: {portal}

ఇట్లు,
[దరఖాస్తుదారుని పేరు / సంతకం]"""
        elif intent == "WELFARE_SCHEME":
            return f"""ప్రభుత్వ సంక్షేమ పథకం ప్రయోజన దరఖాస్తు
సమక్షం: సంబంధిత అధికారి / {forum}

విషయం: {query} పథకం ప్రయోజనాల కొరకు వినతిపత్రం.

అయ్యా,
1. దరఖాస్తుదారు క్రింది ప్రభుత్వ మార్గదర్శకాల ప్రకారం దరఖాస్తు చేస్తున్నారు:
   చట్ట నిబంధనలు: {cit_text} | పోర్టల్: {portal}

2. సమస్య మరియు వివరాలు:
   "{query}"

3. విజ్ఞప్తి: దరఖాస్తును పరిశీలించి అర్హులైన లబ్ధిదారునికి తగిన ప్రయోజనాన్ని అందించాలని ప్రార్థన.

ఇట్లు,
[దరఖాస్తుదారుని పేరు / సంతకం]"""
        else:
            return f"""అధికారిక చట్టపరమైన ఫిర్యాదు / దరఖాస్తు (చిత్తుప్రతి)
సమక్షం: గౌరవనీయ {forum}

విషయం: {query} సంబంధించి చట్టబద్ధమైన న్యాయం మరియు పరిహారం కొరకు.

అయ్యా / అమ్మా,
1. దరఖాస్తుదారు క్రింది చట్టపరమైన నిబంధనల ప్రకారం ఈ ఫిర్యాదును సమర్పిస్తున్నారు:
   చట్ట నిబంధనలు: {cit_text}
   పోర్టల్: {portal} | సమయ పరిమితి: {timeline}

2. ఫిర్యాదు వివరాలు:
   "{query}"

3. విజ్ఞప్తి: జరిగిన ఆర్థిక మరియు మానసిక నష్టానికి తగిన పరిహారాన్ని మంజూరు చేయాల్సిందిగా ప్రార్థన.

ఇట్లు,
[దరఖాస్తుదారుని పేరు / సంతకం]"""

    # -------------------------------------------------------------
    # 6. KANNADA (ಕನ್ನಡ)
    # -------------------------------------------------------------
    elif lang == "kn":
        if intent == "RTI_QUERY":
            return f"""ಮಾಹಿತಿ ಹಕ್ಕು ಕಾಯ್ದೆ ೨೦೦೫ ರ ಅಡಿಯಲ್ಲಿ ಅರ್ಜಿ (ಕಲಂ ೬)
ಮಾನ್ಯ: ಸಾರ್ವಜನಿಕ ಮಾಹಿತಿ ಅಧಿಕಾರಿ (CPIO/SPIO) / {forum}

ವಿಷಯ: {query} ಕುರಿತು ಮಾಹಿತಿ ಒದಗಿಸುವಂತೆ ಕೋರಿಕೆ.

ಮಾನ್ಯರೇ,
೧. ಅರ್ಜಿದಾರರು ಮಾಹಿತಿ ಹಕ್ಕು ಕಾಯ್ದೆಯ ಕಲಂ ೬(೧) ರನ್ವಯ ಕೆಳಗಿನ ಮಾಹಿತಿಯನ್ನು ಕೋರುತ್ತಿದ್ದಾರೆ:
   ಕಾನೂನು ಉಲ್ಲೇಖಗಳು: {cit_text}
   ವಿಲೇವಾರಿ ಅವಧಿ: ಕಲಂ ೭(೧) ರಂತೆ ೩೦ ದಿನಗಳ ಒಳಗೆ

೨. ಕೋರಲಾದ ಮಾಹಿತಿಯ ವಿವರ:
   "{query}"

೩. ಅರ್ಜಿ ಶುಲ್ಕ: ನಿಗದಿತ ₹೧೦ ಶುಲ್ಕ ಪಾವತಿಸಲಾಗಿದೆ. ಪೋರ್ಟಲ್: {portal}

ತಮ್ಮ ವಿಶ್ವಾಸಿ,
[ಅರ್ಜಿದಾರರ ಹೆಸರು / ಸಹಿ]"""
        else:
            return f"""ಕಾನೂನುಬದ್ಧ ದೂರು / ಅರ್ಜಿ (ಕರಡು)
ಮಾನ್ಯ: {forum}

ವಿಷಯ: {query} ಕುರಿತು ಕಾನೂನು ಪರಿಹಾರಕ್ಕಾಗಿ ಅರ್ಜಿ.

ಮಾನ್ಯರೇ,
೧. ಅರ್ಜಿದಾರರು ಈ ಕೆಳಗಿನ ಶಾಸನಬದ್ಧ ಕಲಮುಗಳ ಅಡಿಯಲ್ಲಿ ದೂರನ್ನು ಸಲ್ಲಿಸುತ್ತಿದ್ದಾರೆ:
   ಕಾನೂನು ಉಲ್ಲೇಖಗಳು: {cit_text}
   ದಾಖಲಾತಿ ಪೋರ್ಟಲ್: {portal} | ಶಾಸನಬದ್ಧ ಗಡುವು: {timeline}

೨. ದೂರಿನ ವಿವರ:
   "{query}"

೩. ಪ್ರಾರ್ಥನೆ: ತಕ್ಷಣವೇ ಸೂಕ್ತ ಕ್ರಮ ಕೈಗೊಂಡು ಆದ ಆರ್ಥಿಕ ಮತ್ತು ಮಾನಸಿಕ ತೊಂದರೆಗೆ ಪರಿಹಾರ ನೀಡಬೇಕಾಗಿ ವಿನಂತಿ.

ತಮ್ಮ ವಿಶ್ವಾಸಿ,
[ಅರ್ಜಿದಾರರ ಹೆಸರು / ಸಹಿ]"""

    # -------------------------------------------------------------
    # 7. MALAYALAM (മലയാളം)
    # -------------------------------------------------------------
    elif lang == "ml":
        if intent == "RTI_QUERY":
            return f"""വിവരാവകാശ നിയമം 2005 പ്രകാരമുള്ള അപേക്ഷ (വകുപ്പ് 6)
മുമ്പാകെ: പബ്ലിക് ഇൻഫർമേഷൻ ഓഫീസർ (CPIO/SPIO) / {forum}

വിഷയം: {query} സംബന്ധിച്ച വിവരങ്ങൾ ലഭ്യമാക്കാൻ അപേക്ഷ.

സർ / മാഡം,
1. വിവരാവകാശ നിയമം സെക്ഷൻ 6 പ്രകാരം താഴെ പറയുന്ന വിവരങ്ങൾ നൽകണമെന്ന് അഭ്യർത്ഥിക്കുന്നു:
   നിയമ പരാമർശങ്ങൾ: {cit_text} | സമയപരിധി: 30 ദിവസത്തിനകം

2. ആവശ്യപ്പെടുന്ന വിവരങ്ങൾ:
   "{query}"

3. ഫീസ്: ₹10 നിയമാനുസൃത ഫീസ് ഒടുക്കിയിട്ടുണ്ട്. പോർട്ടൽ: {portal}

വിശ്വസ്തതയോടെ,
[അപേക്ഷകന്റെ പേര് / ഒപ്പ്]"""
        else:
            return f"""ഔദ്യോഗിക നിയമ പരാതി / അപേക്ഷ (കരട്)
മുമ്പാകെ: ബഹുമാനപ്പെട്ട {forum}

വിഷയം: {query} സംബന്ധിച്ച് നിയമപരമായ പരിഹാരം ലഭിക്കുന്നതിനായി.

സർ / മാഡം,
1. അപേക്ഷകൻ താഴെ പറയുന്ന നിയമപരമായ വകുപ്പുകൾ പ്രകാരം ഈ പരാതി സമർപ്പിക്കുന്നു:
   നിയമ പരാമർശങ്ങൾ: {cit_text}
   പോർട്ടൽ: {portal} | സമയപരിധി: {timeline}

2. പരാതിയുടെ വിശദാംಶങ്ങൾ:
   "{query}"

3. അപേക്ഷ: ഉണ്ടായ നഷ്ടങ്ങൾക്കും മാനസിക വിഷമങ്ങൾക്കും അർഹമായ നഷ്ടപരിഹാരം അനുവദിക്കണം.

വിശ്വസ്തതയോടെ,
[അപേക്ഷകന്റെ പേര് / ഒപ്പ്]"""

    # -------------------------------------------------------------
    # 8. GUJARATI (ગુજરાતી)
    # -------------------------------------------------------------
    elif lang == "gu":
        if intent == "RTI_QUERY":
            return f"""માહિતી અધિકાર અધિનિયમ ૨૦૦૫ હેઠળ અરજી (કલમ ૬)
સમક્ષ: જાહેર માહિતી અધિકારી (CPIO/SPIO) / {forum}

વિષય: {query} અંગેની માહિતી મેળવવા બાબત.

મહોદય / મહોદયા,
૧. અરજદાર માહિતી અધિકાર કાયદાની કલમ ૬ મુજબ નીચેની માહિતીની માંગણી કરે છે:
   કાનૂની સંદર્ભ: {cit_text} | નિકાલ સમયમર્યાદા: ૩૦ દિવસ

૨. માંગેલ માહિતીની વિગતો:
   "{query}"

૩. ફી: નિયમ મુજબ ₹૧૦ ફી ચૂકવેલ છે. પોર્ટલ: {portal}

આપનો વિશ્વાસુ,
[અરજદારનું નામ / સહી]"""
        else:
            return f"""ઔપચારિક કાનૂની ફરિયાદ / અરજી (ડ્રાફ્ટ)
સમક્ષ: માનનીય {forum}

વિષય: {query} અંગે કાનૂની નિવારણ મેળવવા બાબત.

મહોદય / મહોદયા,
૧. અરજદાર નીચે મુજબની કાનૂની જોગવાઈઓ હેઠળ આ ફરિયાદ દાખલ કરે છે:
   કાનૂની સંદર્ભ: {cit_text}
   દાખલ પોર્ટલ: {portal} | સમયમર્યાદા: {timeline}

૨. ફરિયાદની વિગતો:
   "{query}"

૩. પ્રાર્થના: સામાવાળાને યોગ્ય આદેશ આપી થયેલા નુકસાન બદલ વળતર મંજૂર કરવામાં આવે.

આપનો વિશ્વાસુ,
[અરજદારનું નામ / સહી]"""

    # -------------------------------------------------------------
    # 9. PUNJABI (ਪੰਜਾਬੀ)
    # -------------------------------------------------------------
    elif lang == "pa":
        if intent == "RTI_QUERY":
            return f"""ਸੂਚਨਾ ਦਾ ਅਧਿਕਾਰ ਐਕਟ 2005 ਤਹਿਤ ਦਰਖ਼ਾਸਤ (ਧਾਰਾ 6)
ਸੇਵਾ ਵਿਖੇ: ਲੋਕ ਸੂਚਨਾ ਅਫ਼ਸਰ (CPIO/SPIO) / {forum}

ਵਿਸ਼ਾ: {query} ਸਬੰਧੀ ਜਾਣਕਾਰੀ ਪ੍ਰਾਪਤ ਕਰਨ ਲਈ।

ਜਨਾਬ / ਸ਼੍ਰੀਮਤੀ ਜੀ,
੧. ਬਿਨੈਕਾਰ ਸੂਚਨਾ ਦਾ ਅਧਿਕਾਰ ਐਕਟ ਦੀ ਧਾਰਾ 6 ਤਹਿਤ ਹੇਠ ਲਿਖੀ ਜਾਣਕਾਰੀ ਦੀ ਮੰਗ ਕਰਦਾ ਹੈ:
   ਕਾਨੂੰਨੀ ਹਵਾਲੇ: {cit_text} | ਨਿਪਟਾਰਾ ਸਮਾਂ: 30 ਦਿਨ

੨. ਲੋੜੀਂਦੀ ਜਾਣਕਾਰੀ ਦਾ ਵੇਰਵਾ:
   "{query}"

੩. ਫ਼ੀਸ: ਨਿਯਮਾਂ ਅਨੁਸਾਰ ₹10 ਫ਼ੀਸ ਜਮ੍ਹਾਂ ਹੈ। ਪੋਰਟਲ: {portal}

ਆਪ ਜੀ ਦਾ ਸ਼ੁਭਚਿੰਤਕ,
[ਬਿਨੈਕਾਰ ਦਾ ਨਾਂ / ਦਸਤਖ਼ਤ]"""
        else:
            return f"""ਰਸਮੀ ਕਾਨੂੰਨੀ ਸ਼ਿਕਾਇਤ / ਅਰਜ਼ੀ (ਡਰਾਫਟ)
ਸੇਵਾ ਵਿਖੇ: ਮਾਣਯੋਗ {forum}

ਵਿਸ਼ਾ: {query} ਸਬੰਧੀ ਕਾਨੂੰਨੀ ਇਨਸਾਫ਼ ਅਤੇ ਹਰਜਾਨੇ ਲਈ।

ਜਨਾਬ / ਸ਼੍ਰੀਮਤੀ ਜੀ,
੧. ਬਿਨੈਕਾਰ ਹੇਠ ਲਿਖੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਤਹਿਤ ਇਹ ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰ ਰਿਹਾ ਹੈ:
   ਕਾਨੂੰਨੀ ਹਵਾਲੇ: {cit_text}
   ਦਾਖ਼ਲ ਪੋਰਟਲ: {portal} | ਕਾਨੂੰਨੀ ਸਮਾਂ: {timeline}

੨. ਸ਼ਿਕਾਇਤ ਦਾ ਵੇਰਵਾ:
   "{query}"

੩. ਬੇਨਤੀ: ਵਿਰੋਧੀ ਧਿਰ ਖ਼ਿਲਾਫ਼ ਤੁਰੰਤ ਹੁਕਮ ਜਾਰੀ ਕਰਕੇ ਬਣਦਾ ਮੁਆਵਜ਼ਾ ਦਿਵਾਇਆ ਜਾਵੇ।

ਆਪ ਜੀ ਦਾ ਸ਼ੁਭਚਿੰਤਕ,
[ਬਿਨੈਕਾਰ ਦਾ ਨਾਂ / ਦਸਤਖ਼ਤ]"""

    # -------------------------------------------------------------
    # 10. ODIA (ଓଡ଼ିଆ)
    # -------------------------------------------------------------
    elif lang == "or":
        if intent == "RTI_QUERY":
            return f"""ସୂଚନା ଅଧିକାର ଆଇନ ୨୦୦୫ ଅଧୀନରେ ଦରଖାସ୍ତ (ଧାରା ୬)
ସମ୍ମୁଖରେ: ଲୋକ ସୂଚନା ଅଧିକାରୀ (CPIO/SPIO) / {forum}

ବିଷୟ: {query} ସମ୍ପର୍କିତ ସୂଚନା ପ୍ରଦାନ ପାଇଁ ଅନୁରୋଧ।

ମହାଶୟ / ମହାଶୟା,
୧. ଆବେଦନକାରୀ ସୂଚନା ଅଧିକାର ଆଇନର ଧାରା ୬(୧) ଅନୁଯାୟୀ ନିମ୍ନ ସୂଚନା ଚାହୁଁଛନ୍ତି:
   ଆଇନଗତ ସନ୍ଦର୍ଭ: {cit_text} | ସମୟସୀମା: ୩୦ ଦିନ

୨. ଆବଶ୍ୟକୀୟ ସୂଚନାର ବିବରଣୀ:
   "{query}"

୩. ଆବେଦନ ଫି: ନିୟମ ଅନୁସାରେ ₹୧୦ ଫି ଦାଖଲ କରାଯାଇଛି। ପୋର୍ଟାଲ: {portal}

ଆପଣଙ୍କର ବିଶ୍ୱସ୍ତ,
[ଆବେଦନକାରୀଙ୍କ ନାମ / ସ୍ୱାକ୍ଷର]"""
        else:
            return f"""ବିଧିବଦ୍ଧ ଆଇନଗତ ଅଭିଯୋଗ / ଦରଖାସ୍ତ (ଖସଡ଼ା)
ସମ୍ମୁଖରେ: ମାନ୍ୟବର {forum}

ବିଷୟ: {query} ସମ୍ପର୍କରେ ନ୍ୟାୟିକ ପ୍ରତିକାର ନିମନ୍ତେ।

ମହାଶୟ / ମହାଶୟା,
୧. ଆବେଦନକାରୀ ନିମ୍ନଲିଖିତ ଆଇନଗତ ଧାରା ଅନୁଯାୟୀ ଏହି ଅଭିଯୋଗ ଦାଖଲ କରୁଛନ୍ତି:
   ଆଇନଗତ ସନ୍ଦର୍ଭ: {cit_text}
   ପୋର୍ଟାଲ: {portal} | ସମୟସୀମା: {timeline}

୨. ଅଭିଯୋଗର ବିବରଣୀ:
   "{query}"

୩. ପ୍ରାର୍ଥନା: ହୋଇଥିବା ମାନସିକ ଓ ଆର୍ଥିକ କ୍ଷତି ପାଇଁ ଉଚିତ କ୍ଷତିପୂରଣ ପ୍ରଦାନ କରାଯାଉ।

ଆପଣଙ୍କର ବିଶ୍ୱସ୍ତ,
[ଆବେଦନକାରୀଙ୍କ ନାମ / ସ୍ୱାକ୍ଷର]"""

    # -------------------------------------------------------------
    # 11. ASSAMESE (অসমীয়া)
    # -------------------------------------------------------------
    elif lang == "as":
        if intent == "RTI_QUERY":
            return f"""তথ্য জনাৰ অধিকাৰ আইন, ২০০৫ ৰ অধীনত আৱেদন (ধাৰা ৬)
প্ৰতি: লোক তথ্য বিষয়া (CPIO/SPIO) / {forum}

বিষয়: {query} সম্পৰ্কে তথ্য প্ৰদানৰ অনুৰোধ।

মহাশয় / মহাশয়া,
১. আৱেদনকাৰীয়ে তথ্য জনাৰ অধিকাৰ আইন ২০০৫ ৰ ধাৰা ৬ অনুসৰি তলত দিয়া তথ্যৰ বাবে অনুৰোধ জনাইছে:
   আইনী প্ৰসংগ: {cit_text} | নিস্পত্তিৰ সময়সীমা: ৩০ দিনৰ ভিতৰত

২. প্ৰয়োজনীয় তথ্যৰ বিৱৰণ:
   "{query}"

৩. আৱেদন মাচুল: ১০ টকাৰ মাচুল সংলগ্ন কৰা হৈছে। পৰ্টেল: {portal}

আপোনাৰ বিশ্বাসী,
[আৱেদনকাৰীৰ নাম / স্বাক্ষৰ]"""
        else:
            return f"""বিধিসন্মত আইনী অভিযোগ / আবেদন (খচৰা)
প্ৰতি: সন্মানীয় {forum}

বিষয়: {query} সম্পৰ্কে আইনী ন্যায় আৰু ক্ষতিপূৰণ বিচাৰি আবেদন।

মহাশয় / মহাশয়া,
১. আবেদনকাৰীয়ে তলত উল্লেখিত আইনী ধাৰা অনুসৰি এই অভিযোগ দাখিল কৰিছে:
   আইনী প্ৰসংগ: {cit_text}
   দাখিলৰ মাধ্যম: {portal} | সময়সীমা: {timeline}

২. অভিযোগৰ বিৱৰণ:
   "{query}"

৩. প্ৰাৰ্থনা: ঘটনাটোৰ উচিত তদন্ত কৰি উপযুক্ত ক্ষতিপূৰণ প্ৰদানৰ আদেশ দিয়ক।

আপোনাৰ বিশ্বাসী,
[আবেদনকাৰীৰ নাম / স্বাক্ষৰ]"""

    # -------------------------------------------------------------
    # 12. URDU (اردو)
    # -------------------------------------------------------------
    elif lang == "ur":
        if intent == "RTI_QUERY":
            return f"""حق معلومات ایکٹ 2005 کے تحت درخواست (دفعہ 6)
بخدمت جناب: پبلک انفارمیشن آفیسر (CPIO/SPIO) / {forum}

موضوع: {query} کے متعلق معلومات کی فراہمی بابت۔

جناب عالی،
1. سائل حق معلومات قانون 2005 کی دفعہ 6 کے تحت مندرجہ ذیل معلومات حاصل کرنے کی درخواست کرتا ہے:
   قانونی حوالہ: {cit_text} | قانونی مدت: 30 یوم کے اندر

2. مطلوبہ معلومات کی تفصیل:
   "{query}"

3. فیس: مقررہ فیس ₹10 ادا کر دی گئی ہے۔ پورٹل: {portal}

المرسل / سائل،
[نام سائل / دستخط]"""
        else:
            return f"""باضابطہ قانونی شکایت / عرضداشت (ڈرافٹ)
بخدمت جناب: معزز {forum}

موضوع: {query} کے متعلق قانونی داد رسی اور ازالۂ نقصان۔

جناب عالی،
1. سائل مندرجہ ذیل قانونی دفعات کے تحت یہ باضابطہ شکایت پیش کر رہا ہے:
   قانونی حوالہ: {cit_text}
   پورٹل: {portal} | مقررہ مدت: {timeline}

2. شکایت کی تفصیلات:
   "{query}"

3. التجا / دعا: معاملے کا فوری نوٹس لے کر سائل کو مناسب ہرجانہ اور معاوضہ دلایا جائے۔

فقط،
[نام سائل / دستخط]"""

    # -------------------------------------------------------------
    # 13. ENGLISH (Default)
    # -------------------------------------------------------------
    else:
        if intent == "RTI_QUERY":
            return f"""APPLICATION UNDER SECTION 6 OF THE RIGHT TO INFORMATION ACT, 2005
BEFORE THE CENTRAL / STATE PUBLIC INFORMATION OFFICER (CPIO / SPIO)
{forum.upper()}

SUBJECT: Request for Information under Section 6(1) regarding {query}

STATUTORY PROVISIONS CITED:
{chr(10).join(['• ' + c for c in citations])}

DETAILS OF INFORMATION SOUGHT:
1. That the Applicant is a citizen of India exercising their statutory right under the RTI Act, 2005.
2. Specific subject matter of inquiry:
   "{query}"
3. Statutory Timeline: Section 7(1) mandates disposal within thirty (30) days of receipt (or 48 hours for life & liberty).

APPLICATION FEE & FILING MODE:
• Prescribed Fee: ₹10 (enclosed via electronic payment / IPO / court fee)
• Portal / Authority: {portal}

Respectfully Submitted,
[Applicant Name & Address Signature]"""
        elif intent == "WELFARE_SCHEME":
            return f"""FORMAL APPLICATION & REPRESENTATION FOR WELFARE SCHEME BENEFIT
BEFORE THE COMPETENT AUTHORITY / NODAL OFFICER
{forum.upper()}

SUBJECT: Representation regarding benefit disbursement and eligibility under {query}

APPLICABLE SCHEME GUIDELINES CITED:
{chr(10).join(['• ' + c for c in citations])}

STATEMENT OF ELIGIBILITY & FACTS:
1. That the Applicant is an eligible citizen seeking legitimate benefit disbursement under government guidelines.
2. Factual background & grievance:
   "{query}"
3. That all mandatory prerequisites (Aadhaar authentication, cultivable landholding, or SECC qualification) are met.

RELIEF PRAYED FOR:
a) Verify the applicant's record and expedite DBT benefit disbursement into the Aadhaar-seeded bank account.
b) Rectify any administrative or portal seeding blockages immediately.

Respectfully Submitted,
[Applicant Name & Contact Signature]
Portal: {portal}"""
        else:
            return f"""FORMAL LEGAL GRIEVANCE & PETITION DRAFT
BEFORE THE HON'BLE {forum.upper()}

IN THE MATTER OF:
Complainant / Applicant vs. Opposite Party / Respondent

SUBJECT: Formal Petition regarding {query}

STATUTORY PROVISIONS CITED:
{chr(10).join(['• ' + c for c in citations])}

PROCEDURAL & JURISDICTIONAL DETAILS:
• Designated Forum / Authority: {forum}
• Pecuniary Jurisdiction: {eligibility.get('pecuniary_limit', 'Statutory Limit')}
• Statutory Timelines: {timeline}
• Official Filing Mode: {portal}

STATEMENT OF FACTS:
1. That the Complainant is an aggrieved citizen approaching this forum under {citations[0] if citations else 'the relevant Act'}.
2. That the grievance arises from the following factual circumstances:
   "{query}"
3. That the aforementioned act of the Opposite Party constitutes a deficiency in service, unfair trade practice, or refusal of statutory duty under law.
4. That the Complainant has suffered significant monetary loss and mental harassment.

PRAYER / RELIEF SOUGHT:
a) Direct the Opposite Party to immediately resolve the grievance, replace defective goods, or provide information requested.
b) Grant refund of consideration paid along with appropriate commercial interest.
c) Award compensation for financial distress and costs of this litigation.
d) Pass any further orders as this Hon'ble Authority may deem just and equitable.

Respectfully Submitted,
[Complainant Name & Contact Signature]
Filing Mode: {portal}"""
