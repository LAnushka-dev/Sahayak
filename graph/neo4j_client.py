import os
from typing import List, Dict, Any, Optional

class KnowledgeGraphClient:
    """
    Neo4j Knowledge Graph connector with dual-mode architecture:
    1. Real Neo4j Bolt Driver (when NEO4J_URI & credentials are provided and neo4j is available)
    2. Local In-Memory Knowledge Graph Engine with Cypher-equivalent traversal & schema
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
        """Pre-seeds the knowledge graph with statutory relationships matching schema.cypher."""
        self.nodes = {
            # Consumer Protection Act 2019
            "CPA_2019": {"type": "Act", "name": "Consumer Protection Act, 2019", "jurisdiction": "India"},
            "CPA_S2_9": {"type": "Section", "number": "Section 2(9)", "title": "Consumer Rights", "act": "CPA_2019"},
            "CPA_S34": {"type": "Section", "number": "Section 34", "title": "Pecuniary Jurisdiction of District Commission", "limit_inr": 5000000, "act": "CPA_2019"},
            "CPA_S35": {"type": "Section", "number": "Section 35", "title": "Filing of Consumer Complaint", "portal": "edaakhil.nic.in", "act": "CPA_2019"},
            "CPA_S38": {"type": "Section", "number": "Section 38", "title": "Procedure on Admission & Defect Analysis", "act": "CPA_2019"},
            "CPA_S47": {"type": "Section", "number": "Section 47", "title": "Jurisdiction of State Commission", "limit_inr": 20000000, "act": "CPA_2019"},
            "CPA_S58": {"type": "Section", "number": "Section 58", "title": "Jurisdiction of National Commission", "act": "CPA_2019"},
            "CPA_S69": {"type": "Section", "number": "Section 69", "title": "Limitation Period (2 Years)", "act": "CPA_2019"},
            "CPA_S84": {"type": "Section", "number": "Section 84", "title": "Product Liability of Manufacturer", "act": "CPA_2019"},
            
            "DCDRC": {"type": "Forum", "name": "District Consumer Disputes Redressal Commission (DCDRC)", "pecuniary_limit": "Up to ₹50 Lakhs", "portal": "edaakhil.nic.in"},
            "SCDRC": {"type": "Forum", "name": "State Consumer Disputes Redressal Commission (SCDRC)", "pecuniary_limit": "₹50 Lakhs to ₹2 Crores", "appeal_authority": "NCDRC"},
            "NCDRC": {"type": "Forum", "name": "National Consumer Disputes Redressal Commission (NCDRC)", "pecuniary_limit": "Above ₹2 Crores", "appeal_authority": "Supreme Court"},
            
            # Right to Information Act 2005
            "RTI_2005": {"type": "Act", "name": "Right to Information Act, 2005", "jurisdiction": "India"},
            "RTI_S6": {"type": "Section", "number": "Section 6", "title": "Filing RTI Application", "fee_inr": 10, "portal": "rtionline.gov.in"},
            "RTI_S7": {"type": "Section", "number": "Section 7(1)", "title": "Disposal Timeline (30 Days / 48 Hours for Life & Liberty)", "timeline_days": 30, "life_liberty_hours": 48},
            "RTI_S8": {"type": "Section", "number": "Section 8", "title": "Exemptions from Disclosure", "grounds": "National Security, Trade Secrets, Personal Privacy"},
            "RTI_S19": {"type": "Section", "number": "Section 19", "title": "First & Second Appeal", "first_appeal_days": 30, "second_appeal_days": 90},
            "RTI_S20": {"type": "Section", "number": "Section 20", "title": "Penalties for Refusal / Delay", "daily_penalty_inr": 250, "max_penalty_inr": 25000},
            
            "CPIO": {"type": "Authority", "name": "Central / State Public Information Officer (CPIO/SPIO)", "timeline": "30 days"},
            "FAA": {"type": "Authority", "name": "First Appellate Authority (FAA)", "timeline": "30-45 days"},
            "CIC": {"type": "Authority", "name": "Central / State Information Commission (CIC/SIC)", "timeline": "Final Statutory Appeal"},
            
            # Central Welfare Schemes
            "PM_KISAN": {"type": "Scheme", "name": "PM-KISAN Samman Nidhi", "annual_benefit_inr": 6000, "installments": 3, "frequency": "₹2000 every 4 months"},
            "CRIT_LAND": {"type": "Criterion", "name": "Cultivable Landholding", "text": "Must own cultivable agricultural land as per state revenue records (Khatoni/7-12)"},
            "CRIT_EKYC": {"type": "Criterion", "name": "Aadhaar eKYC", "text": "Must complete Aadhaar biometric/OTP eKYC and NPCI bank seeding"},
            "EXCL_TAX": {"type": "Exclusion", "name": "Taxpayer Exclusion", "text": "Income tax payers and institutional landholders are excluded"},
            "DOC_LAND": {"type": "Document", "name": "Land Record / 7-12 / RoR"},
            "DOC_AADHAAR": {"type": "Document", "name": "Aadhaar Card with linked Mobile"},
            
            "AYUSHMAN": {"type": "Scheme", "name": "Ayushman Bharat PM-JAY", "coverage_inr": 500000, "benefit": "₹5 Lakh annual secondary/tertiary hospital coverage"},
            "CRIT_SECC": {"type": "Criterion", "name": "SECC 2011 Eligibility", "text": "Vulnerable rural and urban households identified via SECC database"},
            "CRIT_SENIOR": {"type": "Criterion", "name": "Senior Citizen Top-up (70+)", "text": "Universal ₹5 Lakh healthcare cover for all citizens aged 70 and above under Ayushman Vay Vandana"}
        }

        self.edges = [
            # CPA Relationships
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S2_9"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S34"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S35"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S38"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S47"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S58"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S69"},
            {"source": "CPA_2019", "relation": "CONTAINS_SECTION", "target": "CPA_S84"},
            {"source": "CPA_S34", "relation": "DESIGNATES_FORUM", "target": "DCDRC"},
            {"source": "CPA_S35", "relation": "FILED_AT", "target": "DCDRC"},
            {"source": "CPA_S47", "relation": "DESIGNATES_FORUM", "target": "SCDRC"},
            {"source": "CPA_S58", "relation": "DESIGNATES_FORUM", "target": "NCDRC"},
            {"source": "DCDRC", "relation": "APPEAL_TO", "target": "SCDRC"},
            {"source": "SCDRC", "relation": "APPEAL_TO", "target": "NCDRC"},
            
            # RTI Relationships
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S6"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S7"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S8"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S19"},
            {"source": "RTI_2005", "relation": "CONTAINS_SECTION", "target": "RTI_S20"},
            {"source": "RTI_S6", "relation": "DIRECTED_TO", "target": "CPIO"},
            {"source": "RTI_S19", "relation": "FIRST_APPEAL_TO", "target": "FAA"},
            {"source": "RTI_S19", "relation": "SECOND_APPEAL_TO", "target": "CIC"},
            {"source": "CPIO", "relation": "SUBJECT_TO_PENALTY", "target": "RTI_S20"},
            
            # Welfare Schemes
            {"source": "PM_KISAN", "relation": "REQUIRES_CRITERION", "target": "CRIT_LAND"},
            {"source": "PM_KISAN", "relation": "REQUIRES_CRITERION", "target": "CRIT_EKYC"},
            {"source": "PM_KISAN", "relation": "EXCLUDES", "target": "EXCL_TAX"},
            {"source": "CRIT_LAND", "relation": "VERIFIED_BY", "target": "DOC_LAND"},
            {"source": "CRIT_EKYC", "relation": "VERIFIED_BY", "target": "DOC_AADHAAR"},
            
            {"source": "AYUSHMAN", "relation": "REQUIRES_CRITERION", "target": "CRIT_SECC"},
            {"source": "AYUSHMAN", "relation": "INCLUDES_SPECIAL_PROVISION", "target": "CRIT_SENIOR"}
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
                        MATCH (a)-[r]->(b)
                        RETURN a.name AS source_name, type(r) AS relation, b.name AS target_name
                        LIMIT 10
                        """
                    )
                    for rec in res:
                        results.append({
                            "source": rec["source_name"] or "Statutory Authority",
                            "relation": rec["relation"],
                            "target": rec["target_name"] or "Designated Forum"
                        })
                if results:
                    return results
            except Exception as e:
                print(f"[KnowledgeGraph] Cypher execution notice: {e}")

        # Local Graph Traversal
        for edge in self.edges:
            src = self.nodes.get(edge["source"], {})
            tgt = self.nodes.get(edge["target"], {})
            src_str = edge["source"]
            tgt_str = edge["target"]

            matches = False
            if "consumer" in domain_lower or "cpa" in domain_lower or "defect" in domain_lower or "refund" in domain_lower:
                if "CPA" in src_str or "DCDRC" in src_str or "SCDRC" in src_str:
                    matches = True
            elif "rti" in domain_lower or "information" in domain_lower or "cpio" in domain_lower:
                if "RTI" in src_str or "CPIO" in src_str or "FAA" in src_str:
                    matches = True
            elif "scheme" in domain_lower or "kisan" in domain_lower or "ayushman" in domain_lower or "farmer" in domain_lower:
                if "PM_KISAN" in src_str or "AYUSHMAN" in src_str or "CRIT" in src_str:
                    matches = True
            else:
                matches = True

            if matches:
                results.append({
                    "source": src.get("name") or src.get("title") or src.get("number") or edge["source"],
                    "relation": edge["relation"],
                    "target": tgt.get("name") or tgt.get("title") or tgt.get("text") or edge["target"]
                })

        return results[:8]

    def close(self):
        if self.driver:
            self.driver.close()
