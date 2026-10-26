import re
from typing import Dict

class LegalIntentClassifier:
    """
    Multilingual legal intent classifier capable of processing 10 Indian languages + English:
    Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi, Odia, and English.
    """
    def __init__(self):
        self.intent_keywords = {
            "CONSUMER_GRIEVANCE": [
                # English
                "defect", "refund", "warranty", "seller", "refrigerator", "laptop", "delivery", 
                "cheated", "unfair", "consumer", "commission", "damaged", "repair", "refused",
                "broken", "company", "service", "flat", "builder", "car", "tv", "appliance",
                "flipkart", "amazon", "e-commerce", "product", "goods", "shopkeeper",
                # Hindi & Marathi (Devanagari)
                "दुकानदार", "खराब", "तक्रार", "वस्तू", "नुकसान", "ग्राहक", "रिफंड", "वारंटी", "धोखा", "पैसे", "नादुरुस्त",
                # Bengali
                "ত্রুটিযুক্ত", "ফেরত", "ওয়ারেন্টি", "বিক্রেতা", "অভিযোগ", "ক্ষতিপূরণ", "পণ্য",
                # Tamil
                "குறைபாடு", "பணம்", "திரும்ப", "புகார்", "நுகர்வோர்", "சேவை", "வாரண்டி",
                # Telugu
                "లోపం", "రీఫండ్", "వారంటీ", "వినియోగదారు", "ఫిర్యాదు", "నష్టపరిహారం",
                # Kannada
                "ದೋಷ", "ಮರುಪಾವತಿ", "ವಾರಂಟಿ", "ಗ್ರಾಹಕ", "ದೂರು", "ಪರಿಹಾರ",
                # Malayalam
                "തകരാർ", "റീഫണ്ട്", "വാറന്റി", "ഉപഭോക്തൃ", "പരാതി", "നഷ്ടപരിഹാരം",
                # Gujarati
                "ખામી", "રીફંડ", "વોરંટી", "ગ્રાહક", "ફરિયાદ", "નુકસાન",
                # Punjabi
                "ਨੁਕਸ", "ਰਿਫੰਡ", "ਵਾਰੰਟੀ", "ਗਾਹਕ", "ਸ਼ਿਕਾਇਤ", "ਹਰਜਾਨਾ",
                # Odia
                "ତ୍ରୁଟି", "ଟଙ୍କା", "ଫେରସ୍ତ", "ଗ୍ରାହକ", "ଅଭିଯୋଗ", "କ୍ଷତିପୂରଣ"
            ],
            "RTI_QUERY": [
                # English
                "rti", "information", "cpio", "appeal", "budget", "tender", "records", "time limit",
                "officer", "public authority", "first appeal", "second appeal",
                # Hindi & Marathi
                "अधिकार", "माहिती", "अर्ज", "सरकारी", "आरटीआई", "माहिती आयुक्त", "पब्लिक इनफार्मेशन ऑफिसर", "अपील",
                # Bengali
                "তথ্য", "অধিকার", "আবেদন", "আরটিআই", "সরকারি",
                # Tamil
                "தகவல்", "உரிமை", "மனு", "அதிகாரி", "விண்ணப்பம்",
                # Telugu
                "సమాచార", "హక్కు", "దరఖాస్తు", "అధికారి",
                # Kannada
                "ಮಾಹಿತಿ", "ಹಕ್ಕು", "ಅರ್ಜಿ", "ಅಧಿಕಾರಿ",
                # Malayalam
                "വിവരാവകാശ", "അപേക്ഷ", "രേഖകൾ", "ഓഫീസർ",
                # Gujarati
                "માહિતી", "અધિકાર", "અરજી", "અધિકારી",
                # Punjabi
                "ਜਾਣਕਾਰੀ", "ਅਧਿਕਾਰ", "ਅਰਜ਼ੀ", "ਅਫ਼ਸਰ",
                # Odia
                "ସୂଚନା", "ଅଧିକାର", "ଦରଖାସ୍ତ", "ଅଧିକାରୀ"
            ],
            "WELFARE_SCHEME": [
                # English
                "kisan", "pm-kisan", "pmkisan", "ayushman", "scheme", "subsidy", "farmer", "card", "benefit",
                "yojana", "land", "ekyc", "pension", "dbt", "housing", "ration",
                # Hindi & Marathi
                "पंतप्रधान", "शेतकरी", "आरोग्य", "योजना", "जमीन", "पीएम", "किसान", "लाभ", "सबसिडी", "हप्ता", "खाते", "कृषी", "अनुदान",
                # Bengali
                "কৃষক", "যোজনা", "ভর্তুকি", "জমি", "সুবিধা", "আয়ুষ্মান",
                # Tamil
                "விவசாயி", "திட்டம்", "மானியம்", "நிலம்", "ஆயுஷ்மான்",
                # Telugu
                "రైతు", "పథకం", "సబ్సిడీ", "భూమి", "ఆయుష్మాన్",
                # Kannada
                "ರೈತ", "ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ", "ಭೂಮಿ", "ಆಯುಷ್ಮಾನ್",
                # Malayalam
                "കർഷകൻ", "പദ്ധതി", "സബ്‌സിഡി", "ഭൂമി", "ആയുഷ്മാൻ",
                # Gujarati
                "ખેડૂત", "યોજના", "સબસિડી", "જમીન", "આયુષ્માન",
                # Punjabi
                "ਕਿਸਾਨ", "ਯੋਜਨਾ", "ਸਬਸਿਡੀ", "ਜ਼ਮੀਨ", "ਆਯੁਸ਼ਮਾਨ",
                # Odia
                "କୃଷକ", "ଯୋଜନା", "ସବସିଡି", "ଜମି", "ଆୟୁଷ୍ମାନ"
            ]
        }

    def predict(self, query: str) -> Dict[str, any]:
        q_clean = query.lower()
        scores = {"CONSUMER_GRIEVANCE": 0, "RTI_QUERY": 0, "WELFARE_SCHEME": 0}

        for intent, kws in self.intent_keywords.items():
            for kw in kws:
                if kw.lower() in q_clean:
                    scores[intent] += 2

        top_intent = max(scores, key=scores.get)
        confidence = 0.94 if scores[top_intent] > 0 else 0.65
        final_intent = top_intent if scores[top_intent] > 0 else "GENERAL_INQUIRY"

        return {
            "intent": final_intent,
            "confidence": confidence,
            "detected_language": self._detect_language(query)
        }

    def _detect_language(self, text: str) -> str:
        """
        High-precision script-based language identification across 10 Indian scripts.
        """
        # Bengali / Assamese
        if len(re.findall(r'[\u0980-\u09FF]', text)) > 2:
            return "bn"
        # Tamil
        if len(re.findall(r'[\u0B80-\u0BFF]', text)) > 2:
            return "ta"
        # Telugu
        if len(re.findall(r'[\u0C00-\u0C7F]', text)) > 2:
            return "te"
        # Kannada
        if len(re.findall(r'[\u0C80-\u0CFF]', text)) > 2:
            return "kn"
        # Malayalam
        if len(re.findall(r'[\u0D00-\u0D7F]', text)) > 2:
            return "ml"
        # Gujarati
        if len(re.findall(r'[\u0A80-\u0AFF]', text)) > 2:
            return "gu"
        # Punjabi (Gurmukhi)
        if len(re.findall(r'[\u0A00-\u0A7F]', text)) > 2:
            return "pa"
        # Odia
        if len(re.findall(r'[\u0B00-\u0B7F]', text)) > 2:
            return "or"
        # Devanagari (Hindi vs. Marathi)
        if len(re.findall(r'[\u0900-\u097F]', text)) > 2:
            if any(w in text for w in ["आहे", "नाही", "करावी", "माझ्याकडे", "मिळेल", "कोणती", "तक्रार", "झाली", "हप्ता"]):
                return "mr"
            return "hi"

        return "en"
