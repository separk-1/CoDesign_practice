import networkx as nx
import json
import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_FILE_PATH = os.path.join(BASE_DIR, "knowledge_graph.json")
_G = None

def get_graph() -> nx.DiGraph:
    global _G
    if _G is None:
        _G = load_graph()
    return _G

def _normalize_node_link(data: Dict[str, Any]) -> Dict[str, Any]:
    if "links" in data and "edges" not in data:
        data["edges"] = data["links"]
    if "edges" in data and "links" not in data:
        data["links"] = data["edges"]
    return data

def load_graph() -> nx.DiGraph:
    if os.path.exists(GRAPH_FILE_PATH):
        try:
            with open(GRAPH_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            data = _normalize_node_link(data)
            return nx.node_link_graph(data) 
        except Exception as e:
            print(f"Error loading graph: {e}. Creating a new default graph.", flush=True)
            return create_default_knowledge_graph()
    else:
        print("Graph file not found. Creating a new default graph.", flush=True)
        return create_default_knowledge_graph()

def save_graph(graph: nx.DiGraph):
    data = nx.node_link_data(graph)
    data = _normalize_node_link(data)
    with open(GRAPH_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_default_knowledge_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    # Add nodes with basic attributes
    G.add_node("Apple", label="Fruit", description="A sweet, crisp fruit.")
    G.add_node("Banana", label="Fruit", description="A long, curved fruit.")
    G.add_node("Fruit", label="Concept", description="The sweet and fleshy product of a tree or other plant.")
    G.add_node("Red", label="Color", description="The color of blood or fire.")

    # Add edges defining relationships
    G.add_edge("Apple", "Fruit", type="is_a")
    G.add_edge("Banana", "Fruit", type="is_a")
    G.add_edge("Apple", "Red", type="has_color")

    save_graph(G)
    return G
