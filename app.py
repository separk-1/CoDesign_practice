from flask import Flask, request, jsonify, send_from_directory
import os
import traceback
from dotenv import load_dotenv
from openai import OpenAI

import graph_manager as gm
import rag_chain
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

# Load the knowledge graph and initialize OpenAI client
G = gm.get_graph()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Default to a standard model if not specified
MODEL = os.getenv("OPENAI_MODEL_MAIN", "gpt-4o-mini")

@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/ping")
def ping():
    return "pong", 200

@app.get("/api/knowledge-graph")
def knowledge_graph():
    """Returns the graph data in node-link format for visualization."""
    return jsonify(nx.node_link_data(G)), 200

@app.post("/api/chat")
def chat():
    """Handles chat requests, executes RAG, and returns the response."""
    data = request.get_json(silent=True) or {}

    messages = data.get("messages") or []
    if not messages:
        return jsonify({"error": "Missing messages"}), 400

    user_msg = messages[-1].get("content", "").strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    try:
        out = rag_chain.execute_rag_chain(G, user_msg, client, MODEL)
        return jsonify(out), 200
    except Exception as e:
        # Print traceback for debugging purposes
        print(traceback.format_exc())
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run("0.0.0.0", int(os.environ.get("PORT", 5001)), debug=False)
