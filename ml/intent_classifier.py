import os
import re
import pickle
from typing import Dict, Any

class LegalIntentClassifier:
    """
    Multilingual legal intent classifier capable of processing 12 Indian languages + English:
    Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi, Odia, Assamese, Urdu, and English.
    Combines trained ML model representations with high-precision statutory keyword heuristics.
    """
    def __init__(self, model_dir: str = "ml/artifacts"):
        self.model = None
        self.vectorizer = None
        
        # Load trained ML model artifacts if available
        v_path = os.path.join(model_dir, "vectorizer.pkl")
        m_path = os.path.join(model_dir, "intent_model.pkl")
        if os.path.exists(v_path) and os.path.exists(m_path):
            try:
                with open(v_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(m_path, "rb") as f:
                    self.model = pickle.load(f)
            except Exception:
                self.model = None
                self.vectorizer = None

        self.intent_keywords = {
            "CONSUMER_GRIEVANCE": [
                # English
                "defect", "refund", "warranty", "seller", "refrigerator", "laptop", "delivery", 
                "cheated", "unfair", "consumer", "commission", "damaged", "repair", "refused",
                "broken", "company", "service", "flat", "builder", "car", "tv", "appliance",
                "flipkart", "amazon", "e-commerce", "product", "goods", "shopkeeper", "bill",
                "bought", "purchased", "purchase", "supplier", "dealer", "vendor", "manufacturer",
                "equipment", "machine", "breached", "agreement", "delay", "possession",
                # Hindi & Marathi (Devanagari)
                "दुकानदार", "खराब", "तक्रार", "वस्तू", "नुकसान", "ग्राहक", "रिफंड", "वारंटी", "धोखा", "पैसे", "नादुरुस्त", "परतावा",
                # Bengali
                "ত্রুটিযুক্ত", "ফেরত", "ওয়ারেন্টি", "বিক্রেতা", "অভিযোগ", "ক্ষতিপূরণ", "পণ্য", "নষ্ট", "দোকানদার",
                # Assamese
                "ত্ৰুটিপূৰ্ণ", "ভাঙা", "ক্ষতিপূৰণ", "পণ্য", "গ্ৰাহক", "পোহাৰী",
                # Tamil
                "குறைபாடு", "பணம்", "திரும்ப", "புகார்", "நுகர்வோர்", "சேவை", "வாரண்டி", "சேதமடைந்த",
                # Telugu
                "లోపం", "రీఫండ్", "వారంటీ", "వినియోగదారు", "ఫిర్యాదు", "నష్టపరిహారం", "పాడైన",
                # Kannada
                "ದೋಷ", "ಮರುಪಾವತಿ", "ವಾರಂಟಿ", "ಗ್ರಾಹಕ", "ದೂರು", "ಪರಿಹಾರ", "ಕೆಟ್ಟ",
                # Malayalam
                "തകരാർ", "റീഫണ്ട്", "വാറന്റി", "ഉപഭോക്തൃ", "പരാതി", "നഷ്ടപരിഹാരം", "കേടായ",
                # Gujarati
                "ખામી", "રીફંડ", "રિફંડ", "વોરંટી", "ગ્રાહક", "ફરિયાદ", "નુકસાન", "બગડેલું", "ખરાબ", "વોશિંગ", "મશીન", "મોબાઇલ", "દુકાનદાર",
                # Punjabi
                "ਨੁਕਸ", "ਰਿਫੰਡ", "ਵਾਰੰਟੀ", "ਗਾਹਕ", "ਸ਼ਿਕਾਇਤ", "ਹਰਜਾਨਾ", "ਖ਼ਰਾਬ",
                # Odia
                "ତ୍ରୁଟି", "ଟଙ୍କା", "ଫେରସ୍ତ", "ଗ୍ରାହକ", "ଅଭିଯୋଗ", "କ୍ଷତିପୂରଣ", "ନଷ୍ଟ",
                # Urdu
                "نقص", "وارنٹی", "شکایت", "معاوضہ", "صارف", "خراب", "دکاندار", "واپسی"
            ],
            "RTI_QUERY": [
                # English
                "rti", "information", "cpio", "spio", "appeal", "budget", "tender", "records", "time limit",
                "officer", "public authority", "first appeal", "second appeal", "section 6", "section 7",
                # Hindi & Marathi
                "अधिकार", "माहिती", "अर्ज", "सरकारी", "आरटीआई", "माहिती आयुक्त", "पब्लिक इनफार्मेशन ऑफिसर", "अपील", "दंडात्मक",
                # Bengali
                "তথ্য", "অধিকার", "আবেদন", "আরটিআই", "সরকারি", "পাবলিক ইনফরমেশন", "আপিল",
                # Assamese
                "তথ্য", "অধিকাৰ", "আবেদন", "চৰকাৰী", "আৱেদন",
                # Tamil
                "தகவல்", "உரிமை", "மனு", "அதிகாரி", "விண்ணப்பம்", "மேல்முறையீடு",
                # Telugu
                "సమాచార", "హక్కు", "దరఖాస్తు", "అధికారి", "అప్పీలు",
                # Kannada
                "ಮಾಹಿತಿ", "ಹಕ್ಕು", "ಅರ್ಜಿ", "ಅಧಿಕಾರಿ", "ಮೇಲ್ಮನವಿ",
                # Malayalam
                "വിവരാവകാശ", "അപേക്ഷ", "രേഖകൾ", "ഓഫീസർ", "അപ്പീൽ",
                # Gujarati
                "માહિતી", "અધિકાર", "અરજી", "અધિકારી", "અપીલ",
                # Punjabi
                "ਜਾਣਕਾਰੀ", "ਅਧਿਕਾਰ", "ਅਰਜ਼ੀ", "ਅਫ਼ਸਰ", "ਅਪੀਲ",
                # Odia
                "ସୂଚନା", "ଅଧିକାର", "ଦରଖାସ୍ତ", "ଅଧିକାରୀ", "ଅପିଲ",
                # Urdu
                "معلومات", "حق", "درخواست", "آر ٹی آئی", "افسر", "اپیل"
            ],
            "WELFARE_SCHEME": [
                # English
                "kisan", "pm-kisan", "pmkisan", "ayushman", "scheme", "subsidy", "farmer", "card", "benefit",
                "yojana", "land", "ekyc", "pension", "dbt", "housing", "ration", "samman", "hospital",
                # Hindi & Marathi
                "पंतप्रधान", "शेतकरी", "आरोग्य", "योजना", "जमीन", "पीएम", "किसान", "लाभ", "सबसिडी", "हप्ता", "खाते", "कृषी", "अनुदान", "आयुष्मान",
                # Bengali
                "কৃষক", "যোজনা", "ভর্তুকি", "জমি", "সুবিধা", "আয়ুষ্মান", "স্বাস্থ্য", "কিষাণ",
                # Assamese
                "কৃষক", "আঁচনি", "ৰেহাই", "মাটি", "আয়ুষ্মান", "কিষাণ",
                # Tamil
                "விவசாயி", "திட்டம்", "மானியம்", "நிலம்", "ஆயுஷ்மான்", "கிசான்", "சுகாதாரம்",
                # Telugu
                "రైతు", "పథకం", "సబ్సిడీ", "భూమి", "ఆయుష్మాన్", "కిసాన్", "ఆరోగ్య",
                # Kannada
                "ರೈತ", "ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ", "ಭೂಮಿ", "ಆಯುಷ್ಮಾನ್", "ಕಿಸಾನ್", "ಆರೋಗ್ಯ",
                # Malayalam
                "കർഷകൻ", "പദ്ധതി", "സബ്‌സിഡി", "ഭൂമി", "ആയുഷ്മാൻ", "കിസാൻ", "ആരോഗ്യം",
                # Gujarati
                "ખેડૂત", "યોજના", "સબસિડી", "જમીન", "આયુષ્માન", "કિસાન", "આરોગ્ય",
                # Punjabi
                "ਕਿਸਾਨ", "ਯੋਜਨਾ", "ਸਬਸਿਡੀ", "ਜ਼ਮੀਨ", "ਆਯੁਸ਼ਮਾਨ", "ਕਿਸਾਨ", "ਸਿਹਤ",
                # Odia
                "କୃଷକ", "ଯୋଜନା", "ସବସିଡି", "ଜମି", "ଆୟୁଷ୍ମାନ", "କିଷାନ", "ସ୍ୱାସ୍ଥ୍ୟ",
                # Urdu
                "کسان", "اسکیم", "سبسڈی", "زمین", "پی ایم کسان", "آیوشمان", "فائدہ"
            ],
            "GENERAL_INQUIRY": [
                "hello", "hi", "namaste", "timing", "dispensary", "office", "help", "who are you",
                "dispute", "legal aid", "advocate", "lok adalat", "court timing", "contact",
                "नमस्ते", "नमस्कार", "मदत", "वेळ", "সাহায্য", "உதவி", "సహాయం", "ಸಹಾಯ", "സഹായം", "મદદ", "ਮਦਦ", "ସାହାଯ୍ୟ", "مدد"
            ]
        }

    def predict(self, query: str) -> Dict[str, Any]:
        q_clean = query.lower()
        lang = self._detect_language(query)

        # 1. Rule-based keyword matching score
        kw_scores = {"CONSUMER_GRIEVANCE": 0, "RTI_QUERY": 0, "WELFARE_SCHEME": 0, "GENERAL_INQUIRY": 0}
        for intent, kws in self.intent_keywords.items():
            for kw in kws:
                if kw.lower() in q_clean:
                    kw_scores[intent] += 3

        # 2. ML Model Prediction if trained artifact available
        ml_intent = None
        ml_prob = 0.0
        if self.model is not None and self.vectorizer is not None:
            try:
                vec = self.vectorizer.transform([query])
                probs = self.model.predict_proba(vec)[0]
                classes = list(self.model.classes_)
                max_idx = int(probs.argmax())
                ml_intent = classes[max_idx]
                ml_prob = float(probs[max_idx])
            except Exception:
                ml_intent = None

        # Blend scoring
        best_kw_intent = max(kw_scores, key=kw_scores.get)
        best_kw_score = kw_scores[best_kw_intent]

        if best_kw_score >= 3:
            final_intent = best_kw_intent
            confidence = min(0.98, 0.85 + (best_kw_score * 0.02))
        elif ml_intent and ml_prob >= 0.40:
            final_intent = ml_intent
            confidence = round(ml_prob, 2)
        elif best_kw_score > 0:
            final_intent = best_kw_intent
            confidence = 0.75
        else:
            final_intent = "GENERAL_INQUIRY"
            confidence = 0.65

        return {
            "intent": final_intent,
            "confidence": confidence,
            "detected_language": lang
        }

    def _detect_language(self, text: str) -> str:
        """
        High-precision script-based language identification across 12 Indian scripts + English.
        """
        # Urdu / Arabic script
        if len(re.findall(r'[\u0600-\u06FF]', text)) > 2:
            return "ur"
        # Assamese unique characters: ৰ (\u09F0), ৱ (\u09F1)
        if len(re.findall(r'[\u09F0\u09F1]', text)) > 0:
            return "as"
        # Bengali / Eastern Nagari
        if len(re.findall(r'[\u0980-\u09FF]', text)) > 2:
            if any(w in text for w in ["অসম", "নমস্কাৰ", "আঁচনি", "পোহাৰী", "ৰাইজ"]):
                return "as"
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
            if any(w in text for w in ["आहे", "नाही", "करावी", "माझ्याकडे", "मिळेल", "कोणती", "तक्रार", "झाली", "हप्ता", "मध्ये", "झाले", "झाला"]):
                return "mr"
            if any(w in text for w in ["है", "नहीं", "और", "रहा है", "रही है", "किया", "कहा", "दुकानदार ने"]):
                return "hi"
            return "hi"

        return "en"
