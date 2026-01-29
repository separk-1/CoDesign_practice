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


def add_node(graph: nx.DiGraph, node_id: str, attributes: Dict[str, Any]) -> bool:
    if graph.has_node(node_id):
        return False
    graph.add_node(node_id, **attributes)
    save_graph(graph)
    return True

def add_edge(graph: nx.DiGraph, source: str, target: str, attributes: Dict[str, Any]) -> bool:
    if not graph.has_node(source) or not graph.has_node(target):
        return False
    if graph.has_edge(source, target):
        return False
    graph.add_edge(source, target, **attributes)
    save_graph(graph)
    return True

def create_default_knowledge_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    G.add_node("Pump", label="Equipment", description="Pump moves fluid and increases pressure.")
    G.add_node("HEX", label="Equipment", description="Heat exchanger transfers heat between streams.")
    G.add_node("Flow", label="Concept", description="Flow connects equipment through lines.")

    G.add_edge("Pump", "HEX", type="feeds")
    G.add_edge("Flow", "Pump", type="involves")

    save_graph(G)
    return G
