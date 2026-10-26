// Neo4j Knowledge Graph Schema for Sahayak
// Models: Acts, Sections, Forums, Remedies, Welfare Schemes, Eligibility Criteria, and Documents

CREATE CONSTRAINT act_id_unique IF NOT EXISTS FOR (a:Act) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT section_id_unique IF NOT EXISTS FOR (s:Section) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT scheme_id_unique IF NOT EXISTS FOR (sc:Scheme) REQUIRE sc.id IS UNIQUE;
CREATE CONSTRAINT forum_name_unique IF NOT EXISTS FOR (f:Forum) REQUIRE f.name IS UNIQUE;

// 1. Consumer Protection Act 2019 Hierarchy
MERGE (cpa:Act {id: "CPA_2019", name: "Consumer Protection Act, 2019", jurisdiction: "India"})
MERGE (s2:Section {id: "CPA_S2_9", number: "Section 2(9)", title: "Consumer Rights", focus: "Protection, Redressal, Awareness"})
MERGE (s34:Section {id: "CPA_S34", number: "Section 34", title: "Pecuniary Jurisdiction of District Commission", limit_inr: 5000000})
MERGE (s35:Section {id: "CPA_S35", number: "Section 35", title: "Manner of Filing Consumer Complaint", portal: "edaakhil.nic.in"})
MERGE (s47:Section {id: "CPA_S47", number: "Section 47", title: "Jurisdiction of State Commission", limit_inr: 20000000})

MERGE (dist_forum:Forum {name: "District Consumer Disputes Redressal Commission", level: "District", filing_method: "e-Daakhil / Offline"})
MERGE (state_forum:Forum {name: "State Consumer Disputes Redressal Commission", level: "State"})

MERGE (cpa)-[:CONTAINS_SECTION]->(s2)
MERGE (cpa)-[:CONTAINS_SECTION]->(s34)
MERGE (cpa)-[:CONTAINS_SECTION]->(s35)
MERGE (cpa)-[:CONTAINS_SECTION]->(s47)

MERGE (s34)-[:DESIGNATES_FORUM]->(dist_forum)
MERGE (s35)-[:APPLIES_TO_FORUM]->(dist_forum)
MERGE (s47)-[:DESIGNATES_FORUM]->(state_forum)

// 2. Right to Information Act 2005 Hierarchy
MERGE (rti:Act {id: "RTI_2005", name: "Right to Information Act, 2005", jurisdiction: "India"})
MERGE (rti_s6:Section {id: "RTI_S6", number: "Section 6", title: "Request for Information", fee_inr: 10, portal: "rtionline.gov.in"})
MERGE (rti_s7:Section {id: "RTI_S7", number: "Section 7", title: "Disposal of Request", timeline_days: 30, life_liberty_hours: 48})
MERGE (rti_s19:Section {id: "RTI_S19", number: "Section 19", title: "Appeals", first_appeal_days: 30, second_appeal_days: 90})

MERGE (cpio:Authority {name: "Central / State Public Information Officer", role: "Primary Custodian"})
MERGE (faa:Authority {name: "First Appellate Authority", role: "Senior Departmental Officer"})
MERGE (cic:Authority {name: "Central / State Information Commission", role: "Second Appellate Tribunal"})

MERGE (rti)-[:CONTAINS_SECTION]->(rti_s6)
MERGE (rti)-[:CONTAINS_SECTION]->(rti_s7)
MERGE (rti)-[:CONTAINS_SECTION]->(rti_s19)

MERGE (rti_s6)-[:DIRECTED_TO]->(cpio)
MERGE (rti_s19)-[:FIRST_APPEAL_TO]->(faa)
MERGE (rti_s19)-[:SECOND_APPEAL_TO]->(cic)

// 3. Central Welfare Scheme: PM-KISAN
MERGE (pmk:Scheme {id: "PM_KISAN", name: "PM-KISAN Samman Nidhi", annual_benefit_inr: 6000, installments: 3})
MERGE (cond_land:Criterion {name: "Cultivable Landholding", type: "Mandatory", description: "Must own cultivable agricultural land"})
MERGE (cond_ekyc:Criterion {name: "Aadhaar eKYC", type: "Mandatory", description: "Aadhaar linked to bank account and NPCI"})
MERGE (doc_land:RequiredDocument {name: "Khatoni / Land Ownership Records"})
MERGE (doc_aadhaar:RequiredDocument {name: "Aadhaar Card"})

MERGE (pmk)-[:REQUIRES_CRITERION]->(cond_land)
MERGE (pmk)-[:REQUIRES_CRITERION]->(cond_ekyc)
MERGE (cond_land)-[:VERIFIED_BY]->(doc_land)
MERGE (cond_ekyc)-[:VERIFIED_BY]->(doc_aadhaar)
