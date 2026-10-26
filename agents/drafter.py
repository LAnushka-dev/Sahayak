import os
from typing import List, Dict
from agents.state import AgentState

def drafter_node(state: AgentState) -> dict:
    """
    Drafter Agent: Synthesizes retrieved statutory text and citizen grievance to draft
    a formal legal complaint, notice, or application with clause citations in 10 Indian languages + English.
    """
    query = state["query"]
    intent = state.get("intent", "CONSUMER_GRIEVANCE")
    lang = state.get("detected_language", "en")
    docs = state.get("retrieved_documents", [])
    eligibility = state.get("eligibility_status", {})
    trace = state.get("agent_trace", [])

    trace.append(f"[Drafter Agent] Drafting formal petition in language code: '{lang}'...")

    citations = []
    for d in docs:
        text = d.get("text", "")
        if "Section 35" in text:
            citations.append("Consumer Protection Act 2019, Section 35")
        if "Section 34" in text:
            citations.append("Consumer Protection Act 2019, Section 34")
        if "Section 2(9)" in text:
            citations.append("Consumer Protection Act 2019, Section 2(9)")
        if "Section 6" in text:
            citations.append("Right to Information Act 2005, Section 6")
        if "Section 7" in text:
            citations.append("Right to Information Act 2005, Section 7(1)")
        if "Section 19" in text:
            citations.append("Right to Information Act 2005, Section 19")
        if "PM-KISAN" in text:
            citations.append("PM-KISAN Operational Guidelines 2019")
        if "Ayushman" in text:
            citations.append("Ayushman Bharat PM-JAY Operational Guidelines")

    citations = list(set(citations))
    if not citations:
        citations.append("Statutory Grievance Redressal Rules, 2019")

    forum = eligibility.get("recommended_forum", "Appropriate Forum")
    cit_text = ", ".join(citations)

    # 1. MARATHI (मराठी)
    if lang == "mr":
        draft = f"""औपचारिक कायदेशीर तक्रार / अर्ज (मसुदा)
सादर: मा. {forum}

विषय: {query} बाबत वैधानिक दाद मिळणेबाबत.

महोदय / महोदया,
१. अर्जदार खालील अधिकृत कायदेशीर कलमांनुसार ही तक्रार दाखल करत आहे:
   वैधानिक संदर्भ: {cit_text}

२. तक्रारीचा तपशील:
   "{query}"

३. कायदेशीर हक्क व तरतुदी:
   उपरोक्त कायद्यानुसार अर्जदारास योग्य नुकसानभरपाई, सेवा पूर्तता अथवा परतावा मिळण्याचा पूर्ण कायदेशीर हक्क आहे.

४. प्रार्थना / मागणी:
   अ. सदर प्रकरणाची तात्काळ दखल घेऊन योग्य आदेश पारित करावेत.
   ब. झालेल्या आर्थिक व मानसिक त्रासाबद्दल योग्य भरपाई मंजूर करावी.

आपला नम्र,
[अर्जदाराचे नाव / स्वाक्षरी]
दाखल पद्धत: ई-दाखील (edaakhil.nic.in) / आरटीआय पोर्टल (rtionline.gov.in)"""

    # 2. HINDI (हिंदी)
    elif lang == "hi":
        draft = f"""औपचारिक विधिक शिकायत / आवेदन (प्रारूप)
समक्ष: माननीय {forum}

विषय: {query} के संदर्भ में विधिक उपचार एवं निवारण हेतु।

महोदय / महोदया,
१. प्रार्थी इस आवेदन के माध्यम से निम्नलिखित विधिक धाराओं के अंतर्गत शिकायत प्रस्तुत कर रहा है:
   विधिक संदर्भ: {cit_text}

२. शिकायत का विवरण:
   "{query}"

३. विधिक अधिकार:
   संबंधित अधिनियम के अनुसार उपभोक्ता/नागरिक को अनुचित व्यवहार के विरुद्ध पूर्ण विधिक संरक्षण एवं क्षतिपूर्ति का अधिकार है।

४. प्रार्थना:
   क. मामले का त्वरित संज्ञान लेकर विपक्षी को उचित निर्देश दिए जाएं।
   ख. प्रार्थी को हुई आर्थिक व मानसिक क्षति हेतु उचित हर्जाना प्रदान किया जाए।

भवदीय,
[प्रार्थी का नाम / हस्ताक्षर]
दाखिल माध्यम: ई-दाखिल (edaakhil.nic.in) / प्रत्यक्ष आयोग"""

    # 3. BENGALI (বাংলা)
    elif lang == "bn":
        draft = f"""বিধিবদ্ধ আইনি অভিযোগ / আবেদনপত্র (খসড়া)
প্রতি: মাননীয় {forum}

বিষয়: {query} সংক্রান্ত বিষয়ে আইনি প্রতিকার প্রার্থনা।

মহাশয় / মহাশয়া,
১. আবেদনকারী নিম্নলিখিত বিধিবদ্ধ ধারাসমূহের অধীনে এই অভিযোগ দাখিল করছেন:
   আইনি সূত্র: {cit_text}

২. অভিযোগের বিবরণ:
   "{query}"

৩. বিধিবদ্ধ অধিকার:
   প্রাসঙ্গিক আইনানুযায়ী আবেদনকারী ন্যায্য পরিষেবা, ত্রুটিযুক্ত পণ্যের প্রতিস্থাপন বা উপযুক্ত ক্ষতিপূরণ পাওয়ার পূর্ণ অধিকারী।

৪. প্রার্থনা:
   ক. সংশ্লিষ্ট পক্ষকে অবিলম্বে প্রয়োজনীয় ব্যবস্থা গ্রহণ করার নির্দেশ প্রদান করা হোক।
   খ. আবেদনকারীর মানসিক ও আর্থিক ক্ষতির জন্য ন্যায্য ক্ষতিপূরণ মঞ্জুর করা হোক।

বিনীত,
[আবেদনকারীর নাম / স্বাক্ষর]
দাখিলের মাধ্যম: ই-দাখিল পোর্টাল (edaakhil.nic.in)"""

    # 4. TAMIL (தமிழ்)
    elif lang == "ta":
        draft = f"""முறைப்படியான சட்டபூர்வ புகார் மனு (வரைவு)
முன்னிலை: மதிப்பிற்குரிய {forum}

பொருள்: {query} தொடர்பான சட்டபூர்வ நிவாரணம் கோருதல்.

ஐயா / அம்மா,
1. மனுதாரர் பின்வரும் சட்டப் பிரிவுகளின் கீழ் இந்த முறைப்படியான புகாரை சமர்ப்பிக்கிறார்:
   சட்ட குறிப்புகள்: {cit_text}

2. புகாரின் விவரம்:
   "{query}"

3. சட்ட உரிமைகள்:
   சம்பந்தப்பட்ட சட்டங்களின்படி குறைபாடுள்ள சேவை அல்லது நியாயமற்ற வர்த்தக நடைமுறைக்கு எதிராக நிவாரணம் மற்றும் இழப்பீடு பெற மனுதாரருக்கு முழு உரிமை உண்டு.

4. கோரிக்கை:
   அ) எதிர் தரப்பினருக்கு உடனடி தீர்வு வழங்க உத்தரவிடுமாறு வேண்டுகிறேன்.
   ஆ) ஏற்பட்ட இழப்பு மற்றும் மன உளைச்சலுக்கு தகுந்த இழப்பீடு வழங்குமாறு கோருகிறேன்.

இப்படிக்கு,
[மனுதாரர் பெயர் / கையொப்பம்]
தாக்கல் முறை: இ-தாக்கல் இணையதளம் (edaakhil.nic.in)"""

    # 5. TELUGU (తెలుగు)
    elif lang == "te":
        draft = f"""అధికారిక చట్టపరమైన ఫిర్యాదు / దరఖాస్తు (చిత్తుప్రతి)
సమక్షం: గౌరవనీయ {forum}

విషయం: {query} సంబంధించి చట్టబద్ధమైన న్యాయం మరియు పరిహారం కొరకు.

అయ్యా / అమ్మా,
1. దరఖాస్తుదారు క్రింది చట్టపరమైన నిబంధనల ప్రకారం ఈ ఫిర్యాదును సమర్పిస్తున్నారు:
   చట్ట నిబంధనలు: {cit_text}

2. ఫిర్యాదు వివరాలు:
   "{query}"

3. చట్టబద్ధమైన హక్కులు:
   సంబంధిత చట్టం ప్రకారం వినియోగదారునికి/పౌరునికి లోపభూయిష్టమైన సేవల నుండి రక్షణ మరియు నష్టపరిహారం పొందే పూర్తి హక్కు ఉంది.

4. విజ్ఞప్తి:
   ఎ) ఈ ఫిర్యాదును పరిశీలించి ఎదుటి పక్షానికి తగిన ఆదేశాలు జారీ చేయాల్సిందిగా కోరుతున్నాను.
   బి) కలిగిన ఆర్థిక మరియు మానసిక నష్టానికి తగిన పరిహారాన్ని మంజూరు చేయాల్సిందిగా ప్రార్థన.

ఇట్లు,
[దరఖాస్తుదారుని పేరు / సంతకం]
దాఖలు విధానం: ఈ-దాఖిల్ పోర్టల్ (edaakhil.nic.in)"""

    # 6. KANNADA (ಕನ್ನಡ)
    elif lang == "kn":
        draft = f"""ಕಾನೂನುಬದ್ಧ ದೂರು / ಅರ್ಜಿ (ಕರಡು)
ಮಾನ್ಯ: {forum}

ವಿಷಯ: {query} ಕುರಿತು ಕಾನೂನು ಪರಿಹಾರಕ್ಕಾಗಿ ಅರ್ಜಿ.

ಮಾನ್ಯರೇ,
೧. ಅರ್ಜಿದಾರರು ಈ ಕೆಳಗಿನ ಶಾಸನಬದ್ಧ ಕಲಮುಗಳ ಅಡಿಯಲ್ಲಿ ದೂರನ್ನು ಸಲ್ಲಿಸುತ್ತಿದ್ದಾರೆ:
   ಕಾನೂನು ಉಲ್ಲೇಖಗಳು: {cit_text}

೨. ದೂರಿನ ವಿವರ:
   "{query}"

೩. ಕಾನೂನುಬದ್ಧ ಹಕ್ಕುಗಳು:
   ಸಂಬಂಧಿತ ಕಾಯ್ದೆಯನ್ವಯ ಅರ್ಜಿದಾರರಿಗೆ ನ್ಯೂನತೆಯುಳ್ಳ ಸೇವೆ ವಿರುದ್ಧ ನ್ಯಾಯಯುತ ಪರಿಹಾರ ಹಾಗೂ ಮರುಪಾವತಿ ಪಡೆಯುವ ಸಂಪೂರ್ಣ ಹಕ್ಕಿದೆ.

೪. ಪ್ರಾರ್ಥನೆ:
   ಅ) ಎದುರು ಪಕ್ಷಕ್ಕೆ ತಕ್ಷಣವೇ ಕ್ರಮ ಕೈಗೊಳ್ಳಲು ಆದೇಶಿಸಬೇಕಾಗಿ ವಿನಂತಿ.
   ಆ) ಆದ ಆರ್ಥಿಕ ಮತ್ತು ಮಾನಸಿಕ ತೊಂದರೆಗೆ ಸೂಕ್ತ ಪರಿಹಾರ ನೀಡಬೇಕಾಗಿ ಪ್ರಾರ್ಥನೆ.

ತಮ್ಮ ವಿಶ್ವಾಸಿ,
[ಅರ್ಜಿದಾರರ ಹೆಸರು / ಸಹಿ]
ದಾಖಲಾತಿ ವಿಧಾನ: ಇ-ದಾಖಿಲ್ ಪೋರ್ಟಲ್ (edaakhil.nic.in)"""

    # 7. MALAYALAM (മലയാളം)
    elif lang == "ml":
        draft = f"""ഔദ്യോഗിക നിയമ പരാതി / അപേക്ഷ (കരട്)
മുമ്പാകെ: ബഹുമാനപ്പെട്ട {forum}

വിഷയം: {query} സംബന്ധിച്ച് നിയമപരമായ പരിഹാരം ലഭിക്കുന്നതിനായി.

സർ / മാഡം,
1. അപേക്ഷകൻ താഴെ പറയുന്ന നിയമപരമായ വകുപ്പുകൾ പ്രകാരം ഈ പരാതി സമർപ്പിക്കുന്നു:
   നിയമ പരാമർശങ്ങൾ: {cit_text}

2. പരാതിയുടെ വിശദാംശങ്ങൾ:
   "{query}"

3. നിയമപരമായ അവകാശങ്ങൾ:
   ഉപഭോക്തൃ സംരക്ഷണ നിയമപ്രകാരം തകരാറുള്ള സേവനത്തിനെതിരെ നഷ്ടപരിഹാരത്തിനും റീഫണ്ടിനും അപേക്ഷകന് പൂർണ്ണ അവകാശമുണ്ട്.

4. അപേക്ഷ / പ്രാർത്ഥന:
   എ) പരാതിയിൽ അടിയന്തരമായി ഉത്തരവ് പുറപ്പെടുവിക്കണമെന്ന് അഭ്യർത്ഥിക്കുന്നു.
   ബി) ഉണ്ടായ നഷ്ടങ്ങൾക്കും മാനസിക വിഷമങ്ങൾക്കും അർഹമായ നഷ്ടപരിഹാരം അനുവദിക്കണം.

വിശ്വസ്തതയോടെ,
[അപേക്ഷകന്റെ പേര് / ഒപ്പ്]
സമർപ്പണ രീതി: ഇ-ദാഖിൽ പോർട്ടൽ (edaakhil.nic.in)"""

    # 8. GUJARATI (ગુજરાતી)
    elif lang == "gu":
        draft = f"""ઔપચારિક કાનૂની ફરિયાદ / અરજી (ડ્રાફ્ટ)
સમક્ષ: માનનીય {forum}

વિષય: {query} અંગે કાનૂની નિવારણ મેળવવા બાબત.

મહોદય / મહોદયા,
૧. અરજદાર નીચે મુજબની કાનૂની જોગવાઈઓ હેઠળ આ ફરિયાદ દાખલ કરે છે:
   કાનૂની સંદર્ભ: {cit_text}

૨. ફરિયાદની વિગતો:
   "{query}"

૩. કાનૂની અધિકાર:
   સંબંધિત કાયદા અનુસાર ગ્રાહકને ખામીયુક્ત સેવા સામે યોગ્ય વળતર અને ન્યાય મેળવવાનો સંપૂર્ણ વૈધાનિક અધિકાર છે.

૪. પ્રાર્થના:
   અ. સામાવાળાને યોગ્ય આદેશ આપી ત્વરિત નિવારણ કરવામાં આવે.
   બ. થયેલા નુકસાન અને માનસિક ત્રાસ બદલ યોગ્ય વળતર મંજૂર કરવામાં આવે.

આપનો વિશ્વાસુ,
[અરજદારનું નામ / સહી]
દાખલ પદ્ધતિ: ઈ-દાખિલ પોર્ટલ (edaakhil.nic.in)"""

    # 9. PUNJABI (ਪੰਜਾਬੀ)
    elif lang == "pa":
        draft = f"""ਰਸਮੀ ਕਾਨੂੰਨੀ ਸ਼ਿਕਾਇਤ / ਅਰਜ਼ੀ (ਡਰਾਫਟ)
ਸੇਵਾ ਵਿਖੇ: ਮਾਣਯੋਗ {forum}

ਵਿਸ਼ਾ: {query} ਸਬੰਧੀ ਕਾਨੂੰਨੀ ਇਨਸਾਫ਼ ਅਤੇ ਹਰਜਾਨੇ ਲਈ।

ਜਨਾਬ / ਸ਼੍ਰੀਮਤੀ ਜੀ,
੧. ਬਿਨੈਕਾਰ ਹੇਠ ਲਿਖੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਤਹਿਤ ਇਹ ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰ ਰਿਹਾ ਹੈ:
   ਕਾਨੂੰਨੀ ਹਵਾਲੇ: {cit_text}

੨. ਸ਼ਿਕਾਇਤ ਦਾ ਵੇਰਵਾ:
   "{query}"

੩. ਕਾਨੂੰਨੀ ਹੱਕ:
   ਸਬੰਧਤ ਐਕਟ ਅਨੁਸਾਰ ਖ਼ਪਤਕਾਰ ਨੂੰ ਨੁਕਸਦਾਰ ਸੇਵਾ ਦੇ ਖ਼ਿਲਾਫ਼ ਪੂਰਾ ਹਰਜਾਨਾ ਅਤੇ ਰਿਫੰਡ ਲੈਣ ਦਾ ਕਾਨੂੰਨੀ ਅਧਿਕਾਰ ਹੈ।

੪. ਬੇਨਤੀ / ਰਾਹਤ:
   ੳ) ਵਿਰੋਧੀ ਧਿਰ ਨੂੰ ਤੁਰੰਤ ਸ਼ਿਕਾਇਤ ਦਾ ਨਿਪਟਾਰਾ ਕਰਨ ਦਾ ਹੁਕਮ ਦਿੱਤਾ ਜਾਵੇ।
   ਅ) ਹੋਏ ਆਰਥਿਕ ਅਤੇ ਮਾਨਸਿਕ ਨੁਕਸਾਨ ਦਾ ਬਣਦਾ ਮੁਆਵਜ਼ਾ ਦਿਵਾਇਆ ਜਾਵੇ।

ਆਪ ਜੀ ਦਾ ਸ਼ੁਭਚਿੰਤਕ,
[ਬਿਨੈਕਾਰ ਦਾ ਨਾਂ / ਦਸਤਖ਼ਤ]
ਦਾਖ਼ਲ ਕਰਨ ਦਾ ਢੰਗ: ਈ-ਦਾਖ਼ਿਲ ਪੋਰਟਲ (edaakhil.nic.in)"""

    # 10. ODIA (ଓଡ଼ିଆ)
    elif lang == "or":
        draft = f"""ବିଧିବଦ୍ଧ ଆଇନଗତ ଅଭିଯୋଗ / ଦରଖାସ୍ତ (ଖସଡ଼ା)
ସମ୍ମୁଖରେ: ମାନ୍ୟବର {forum}

ବିଷୟ: {query} ସମ୍ପର୍କରେ ନ୍ୟାୟିକ ପ୍ରତିକାର ନିମନ୍ତେ।

ମହାଶୟ / ମହାଶୟା,
୧. ଆବେଦନକାରୀ ନିମ୍ନଲିଖିତ ଆଇନଗତ ଧାରା ଅନୁଯାୟୀ ଏହି ଅଭିଯୋଗ ଦାଖଲ କରୁଛନ୍ତି:
   ଆଇନଗତ ସନ୍ଦର୍ଭ: {cit_text}

୨. ଅଭିଯୋଗର ବିବରଣୀ:
   "{query}"

୩. ଆଇନଗତ ଅଧିକାର:
   ଉପଭୋକ୍ତା ସୁରକ୍ଷା ଆଇନ ଅନୁଯାୟୀ ତ୍ରୁଟିପୂର୍ଣ୍ଣ ସେବା ବିରୁଦ୍ଧରେ ଆବେଦନକାରୀଙ୍କୁ କ୍ଷତିପୂରଣ ଏବଂ ଟଙ୍କା ଫେରସ୍ତ ପାଇବାର ସମ୍ପୂର୍ଣ୍ଣ ଅଧିକାର ରହିଛି।

୪. ପ୍ରାର୍ଥନା:
   କ) ବିପକ୍ଷ ପାର୍ଟିକୁ ତୁରନ୍ତ ସମସ୍ୟାର ସମାଧାନ କରିବାକୁ ନିର୍ଦ୍ଦେଶ ଦିଆଯାଉ।
   ଖ) ହୋଇଥିବା ମାନସିକ ଓ ଆର୍ଥିକ କ୍ଷତି ପାଇଁ ଉଚିତ କ୍ଷତିପୂରଣ ପ୍ରଦାନ କରାଯାଉ।

ଆପଣଙ୍କର ବିଶ୍ୱସ୍ତ,
[ଆବେଦନକାରୀଙ୍କ ନାମ / ସ୍ୱାକ୍ଷର]
ଦାଖଲ ପଦ୍ଧତି: ଇ-ଦାଖିଲ ପୋର୍ଟାଲ (edaakhil.nic.in)"""

    # 11. ENGLISH (Default)
    else:
        draft = f"""FORMAL LEGAL GRIEVANCE & PETITION DRAFT
BEFORE THE HON'BLE {forum.upper()}

IN THE MATTER OF:
Complainant / Applicant vs. Opposite Party

SUBJECT: Grievance regarding {query}

STATUTORY PROVISIONS CITED:
{chr(10).join(['• ' + c for c in citations])}

STATEMENT OF FACTS:
1. That the Complainant is an aggrieved citizen approaching this forum under {citations[0] if citations else 'the relevant Act'}.
2. That the grievance arises from the following circumstances:
   "{query}"
3. That the aforementioned acts of the Opposite Party constitute an infringement of statutory rights, deficiency of service, or failure of public duty.

PRAYER / RELIEF SOUGHT:
a) Direct the Opposite Party to immediately resolve the grievance and rectify the deficiency.
b) Grant appropriate refund and compensation for financial and mental harassment incurred.
c) Pass any further order this Hon'ble Forum deems fit in the interest of justice.

Respectfully Submitted,
[Complainant Name & Contact]
Filing Mode: Online (edaakhil.nic.in / rtionline.gov.in) or Offline In-Person"""

    trace.append(f"[Drafter Agent] Draft completed in language '{lang}' with {len(citations)} statutory citations.")

    return {
        "draft_petition": draft.strip(),
        "citations": citations,
        "agent_trace": trace
    }
