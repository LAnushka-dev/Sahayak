import os
from typing import List, Dict, Any, Optional

class KnowledgeGraphClient:
    """
    Neo4j Knowledge Graph connector with dual-mode architecture:
    1. Real Neo4j Bolt Driver (when NEO4J_URI & credentials are provided)
    2. Local In-Memory Knowledge Graph Engine with Cypher-equivalent traversal
    """
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = None
        self.is_connected = False
        
        # In-memory graph nodes and edges
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, str]] = []
        
        self._try_connect_neo4j()
        self._seed_local_graph()

    def _try_connect_neo4j(self):
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.is_connected = True
            print("[KnowledgeGraph] Connected to live Neo4j instance.")
        except Exception:
            self.is_connected = False
            self.driver = None
            print("[KnowledgeGraph] Operating in high-performance local Graph Engine mode.")

    def _seed_local_graph(self):
        """Pre-seeds the knowledge graph with statutory relationships."""
        # Nodes
        self.nodes = {
            "CPA_2019": {"type": "Act", "name": "Consumer Protection Act, 2019", "jurisdiction": "India"},
            "CPA_S2_9": {"type": "Section", "number": "Section 2(9)", "title": "Consumer Rights", "act": "CPA_2019"},
            "CPA_S34": {"type": "Section", "number": "Section 34", "title": "Pecuniary Jurisdiction", "limit_inr": 5000000, "act": "CPA_2019"},
            "CPA_S35": {"type": "Section", "number": "Section 35", "title": "Filing of Consumer Complaint", "portal": "edaakhil.nic.in", "act": "CPA_2019"},
            "DCDRC": {"type": "Forum", "name": "District Consumer Commission", "limit_inr": 5000000, "appeal_authority": "SCDRC"},
            "SCDRC": {"type": "Forum", "name": "State Consumer Commission", "limit_inr": 20000000, "appeal_authority": "NCDRC"},
            
            "RTI_2005": {"type": "Act", "name": "Right to Information Act, 2005", "jurisdiction": "India"},
            "RTI_S6": {"type": "Section", "number": "Section 6", "title": "Filing RTI Request", "fee": 10, "portal": "rtionline.gov.in"},
            "RTI_S7": {"type": "Section", "number": "Section 7", "title": "Disposal Timeline", "days": 30, "life_liberty_hours": 48},
            "RTI_S19": {"type": "Section", "number": "Section 19", "title": "First & Second Appeal", "first_appeal_days": 30},
            
            "PM_KISAN": {"type": "Scheme", "name": "PM-KISAN Samman Nidhi", "annual_benefit": 6000, "frequency": "3 installments of ₹2000"},
            "CRIT_LAND": {"type": "EligibilityCriterion", "text": "Must own cultivable agricultural land as per state revenue records"},
            "CRIT_EKYC": {"type": "EligibilityCriterion", "text": "Must complete Aadhaar biometric/OTP eKYC and NPCI bank seeding"},
            "EXCL_TAX": {"type": "Exclusion", "text": "Income tax payers and institutional landholders are excluded"}
        }

        # Edges
        self.edges = [
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S2_9"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S34"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S35"},
            {"source": "CPA_S34", "relation": "DIRECTS_TO", "target": "DCDRC"},
            {"source": "CPA_S35", "relation": "FILED_AT", "target": "DCDRC"},
            {"source": "DCDRC", "relation": "APPEAL_TO", "target": "SCDRC"},
            
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S6"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S7"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S19"},
            
            {"source": "PM_KISAN", "relation": "REQUIRES_CRITERION", "target": "CRIT_LAND"},
            {"source": "PM_KISAN", "relation": "REQUIRES_CRITERION", "target": "CRIT_EKYC"},
            {"source": "PM_KISAN", "relation": "EXCLUDES", "target": "EXCL_TAX"}
        ]

    def query_graph_for_remedy(self, domain: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph to return legal remedies, forums, and governing sections for a given domain.
        """
        results = []
        domain_lower = domain.lower()

        # If live Neo4j is connected, execute Cypher
        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    res = session.run(
                        """
                        MATCH (a:Act)-[:CONTAINS_SECTION]->(s:Section)-[r]->(f:Forum)
                        RETURN a.name AS act, s.number AS section, s.title AS title, f.name AS forum
                        LIMIT 5
                        """
                    )
                    for rec in res:
                        results.append({
                            "act": rec["act"],
                            "section": rec["section"],
                            "title": rec["title"],
                            "forum": rec["forum"]
                        })
                if results:
                    return results
            except Exception as e:
                print(f"[KnowledgeGraph] Cypher execution error: {e}")

        # Local Graph Traversal
        for edge in self.edges:
            src = self.nodes.get(edge["source"], {})
            tgt = self.nodes.get(edge["target"], {})
            if "consumer" in domain_lower and "CPA" in edge["source"]:
                results.append({
                    "source": src.get("name") or src.get("title") or edge["source"],
                    "relation": edge["relation"],
                    "target": tgt.get("name") or tgt.get("title") or tgt.get("text") or edge["target"]
                })
            elif ("rti" in domain_lower or "information" in domain_lower) and "RTI" in edge["source"]:
                results.append({
                    "source": src.get("name") or src.get("title") or edge["source"],
                    "relation": edge["relation"],
                    "target": tgt.get("name") or tgt.get("title") or tgt.get("text") or edge["target"]
                })
            elif ("scheme" in domain_lower or "kisan" in domain_lower or "farmer" in domain_lower) and "PM_KISAN" in edge["source"]:
                results.append({
                    "source": src.get("name") or src.get("title") or edge["source"],
                    "relation": edge["relation"],
                    "target": tgt.get("name") or tgt.get("title") or tgt.get("text") or edge["target"]
                })

        return results[:5]

    def close(self):
        if self.driver:
            self.driver.close()
