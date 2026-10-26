import sys
import os

def main():
    if len(sys.argv) < 2:
        print("""
======================================================
     SAHAYAK - Multimodal Agentic Graph-RAG System
======================================================
Usage:
  python run.py demo    -> Launch Interactive Gradio Web UI (Port 7860)
  python run.py api     -> Launch FastAPI REST Backend (Port 8000)
  python run.py eval    -> Run RAGAS Benchmark Evaluation
  python run.py train   -> Run ML Transformer Intent Training & Benchmark
  python run.py test    -> Run End-to-End Pipeline Sanity Check
======================================================
""")
        sys.argv.append("demo")

    cmd = sys.argv[1].lower()

    if cmd == "demo":
        print("[Sahayak] Starting Gradio Interactive Demo...")
        import subprocess
        subprocess.run([sys.executable, "demo/app_gradio.py"])

    elif cmd == "api":
        print("[Sahayak] Starting FastAPI Server with Uvicorn on http://127.0.0.1:8000 ...")
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

    elif cmd == "eval":
        print("[Sahayak] Running RAGAS Evaluation on 40 Benchmark Queries...")
        from eval.run_ragas import evaluate_pipeline
        evaluate_pipeline()

    elif cmd == "train":
        print("[Sahayak] Running ML Intent Classifier Training & Baseline Comparison...")
        from ml.train_classifier import train_tfidf_baseline, simulate_transformer_finetuning
        train_tfidf_baseline()
        simulate_transformer_finetuning()

    elif cmd == "test":
        print("[Sahayak] Running End-to-End System Sanity Check...")
        from agents.orchestrator import run_sahayak
        res = run_sahayak("I bought a damaged TV for Rs 45000 and the company refused repair.")
        print("Intent:", res.get("intent"))
        print("Forum:", res.get("eligibility_status", {}).get("recommended_forum"))
        print("Citations:", res.get("citations"))
        print("Grounded Status:", res.get("is_grounded"))
        print("Agent Trace Steps:", len(res.get("agent_trace", [])))
        print("\n[SUCCESS] All systems operational!")

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
