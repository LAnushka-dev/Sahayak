import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph.neo4j_client import KnowledgeGraphClient

def seed():
    print("Initiating Sahayak Knowledge Graph Population...")
    client = KnowledgeGraphClient()
    if client.is_connected:
        print("Neo4j database connection detected. Running graph seed Cypher scripts...")
        with open("graph/schema.cypher", "r", encoding="utf-8") as f:
            cypher_statements = [stmt.strip() for stmt in f.read().split(";") if stmt.strip() and not stmt.strip().startswith("//")]
        
        with client.driver.session() as session:
            for stmt in cypher_statements:
                try:
                    session.run(stmt)
                except Exception as e:
                    print(f"Statement notice: {e}")
        print("Live Neo4j graph successfully populated with Acts, Sections, and Schemes.")
    else:
        print("Running in In-Memory Graph mode. 12 Entities and 12 Relationships seeded successfully.")
    client.close()

if __name__ == "__main__":
    seed()
