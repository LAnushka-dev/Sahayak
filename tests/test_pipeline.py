import os
import sys
import unittest

# Ensure workspace root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import run_sahayak
from ml.intent_classifier import LegalIntentClassifier
from graph.neo4j_client import KnowledgeGraphClient
from rag.embeddings import MultilingualEmbeddings
from rag.vector_store import FAISSVectorStore
from rag.bm25 import BM25Retriever
from backend.main import app

class TestSahayakPipeline(unittest.TestCase):

    def test_intent_classifier(self):
        clf = LegalIntentClassifier()
        res1 = clf.predict("I bought a damaged refrigerator for Rs 25000 and the company refuses refund.")
        self.assertEqual(res1["intent"], "CONSUMER_GRIEVANCE")
        self.assertEqual(res1["detected_language"], "en")

        res2 = clf.predict("How to file an RTI application under Section 6 to see public accounts?")
        self.assertEqual(res2["intent"], "RTI_QUERY")

        res3 = clf.predict("माझ्याकडे २ एकर जमीन आहे, मला पीएम किसान योजनेचा लाभ कसा मिळेल?")
        self.assertEqual(res3["intent"], "WELFARE_SCHEME")
        self.assertEqual(res3["detected_language"], "mr")

    def test_knowledge_graph_traversal(self):
        kg = KnowledgeGraphClient()
        consumer_paths = kg.query_graph_for_remedy("consumer")
        self.assertGreater(len(consumer_paths), 0)
        self.assertTrue(any("CPA" in str(p) or "Consumer" in str(p) or "Commission" in str(p) for p in consumer_paths))

        rti_paths = kg.query_graph_for_remedy("rti")
        self.assertGreater(len(rti_paths), 0)
        self.assertTrue(any("RTI" in str(p) or "Information" in str(p) or "CPIO" in str(p) for p in rti_paths))

    def test_vector_store_and_bm25(self):
        embeddings = MultilingualEmbeddings()
        vs = FAISSVectorStore(embeddings)
        docs = [
            "Under Section 34 of the Consumer Protection Act 2019, District Commission entertains complaints up to 50 Lakhs.",
            "Under Section 7 of the RTI Act 2005, information must be provided within 30 days.",
            "PM-KISAN Samman Nidhi provides Rs 6000 per year to small and marginal farmers."
        ]
        vs.add_texts(docs)
        hits = vs.similarity_search("District Commission pecuniary limit 50 lakhs", top_k=2)
        self.assertGreater(len(hits), 0)
        self.assertIn("Section 34", hits[0][0])

        bm25 = BM25Retriever()
        bm25.fit(docs)
        bm_hits = bm25.search("RTI Act 30 days information", top_k=2)
        self.assertGreater(len(bm_hits), 0)
        self.assertIn("Section 7", bm_hits[0]["document"])

    def test_langgraph_multi_agent_pipeline(self):
        res = run_sahayak("I bought an air conditioner for Rs 35,000 and it stopped working after 3 days. Dealer refuses replacement.")
        self.assertEqual(res["intent"], "CONSUMER_GRIEVANCE")
        self.assertIn("District", res["eligibility_status"]["recommended_forum"])
        self.assertGreater(len(res["citations"]), 0)
        self.assertTrue(res["is_grounded"])
        self.assertIsNotNone(res["draft_petition"])
        self.assertGreaterEqual(len(res["agent_trace"]), 5)

    def test_pecuniary_routing(self):
        # Above 50 Lakhs -> SCDRC
        res_state = run_sahayak("I bought a luxury apartment for Rs 7500000 and builder delayed possession.")
        self.assertIn("State", res_state["eligibility_status"]["recommended_forum"])
        self.assertIn("Section 47", "; ".join(res_state["citations"]))

        # Above 2 Crores -> NCDRC
        res_nat = run_sahayak("Commercial equipment purchase worth Rs 25000000 arrived defective from manufacturer.")
        self.assertIn("National", res_nat["eligibility_status"]["recommended_forum"])
        self.assertIn("Section 58", "; ".join(res_nat["citations"]))

    def test_multilingual_drafting(self):
        res_hi = run_sahayak("दुकानदार ने खराब मोबाइल दिया और पैसे वापस करने से मना कर रहा है", preferred_language="hi")
        self.assertEqual(res_hi["detected_language"], "hi")
        self.assertIn("शिकायत", res_hi["draft_petition"])

        res_mr = run_sahayak("माझ्याकडे २ एकर जमीन आहे, मला पीएम किसान योजनेचा लाभ कसा मिळेल?", preferred_language="mr")
        self.assertEqual(res_mr["detected_language"], "mr")
        self.assertTrue("तक्रार" in res_mr["draft_petition"] or "अर्ज" in res_mr["draft_petition"])

    def test_fastapi_endpoints(self):
        # Test using Starlette / FastAPI TestClient if installed, or direct function calls
        from backend.main import root, health, chat_endpoint
        from backend.schemas import ChatRequest

        r_root = root()
        self.assertEqual(r_root["service"], "Sahayak Backend")

        r_health = health()
        self.assertEqual(r_health["status"], "healthy")

        req = ChatRequest(query="How to file an RTI request under Section 6?")
        chat_res = chat_endpoint(req)
        self.assertEqual(chat_res["intent"], "RTI_QUERY")
        self.assertGreater(len(chat_res["citations"]), 0)
        self.assertTrue(chat_res["is_grounded"])

if __name__ == "__main__":
    unittest.main()
