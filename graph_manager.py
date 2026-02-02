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

    # --- Nodes ---

    # Movies
    G.add_node("Inception", label="Movie", description="A thief who steals corporate secrets through the use of dream-sharing technology.")
    G.add_node("Titanic", label="Movie", description="A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.")
    G.add_node("The Matrix", label="Movie", description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.")
    G.add_node("Interstellar", label="Movie", description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.")

    # People (Actors/Directors)
    G.add_node("Leonardo DiCaprio", label="Person", description="American actor and film producer. Known for Titanic and Inception.")
    G.add_node("Christopher Nolan", label="Person", description="British-American film director, producer, and screenwriter. Known for Inception and Interstellar.")
    G.add_node("Kate Winslet", label="Person", description="English actress. Known for Titanic.")
    G.add_node("James Cameron", label="Person", description="Canadian filmmaker. Directed Titanic.")
    G.add_node("Keanu Reeves", label="Person", description="Canadian actor. Known for The Matrix.")
    G.add_node("Lana Wachowski", label="Person", description="American film director. Directed The Matrix.")
    G.add_node("Ellen Page", label="Person", description="Canadian actress. Acted in Inception.")

    # Genres
    G.add_node("Sci-Fi", label="Genre", description="Science fiction is a genre of speculative fiction.")
    G.add_node("Romance", label="Genre", description="Romance films involve romantic love stories recorded in visual media.")
    G.add_node("Action", label="Genre", description="Action film is a film genre in which the protagonist is thrust into a series of events that typically include violence and physical feats.")

    # --- Edges ---

    # Relationships for Inception
    G.add_edge("Leonardo DiCaprio", "Inception", type="ACTED_IN")
    G.add_edge("Ellen Page", "Inception", type="ACTED_IN")
    G.add_edge("Christopher Nolan", "Inception", type="DIRECTED")
    G.add_edge("Inception", "Sci-Fi", type="HAS_GENRE")
    G.add_edge("Inception", "Action", type="HAS_GENRE")

    # Relationships for Titanic
    G.add_edge("Leonardo DiCaprio", "Titanic", type="ACTED_IN")
    G.add_edge("Kate Winslet", "Titanic", type="ACTED_IN")
    G.add_edge("James Cameron", "Titanic", type="DIRECTED")
    G.add_edge("Titanic", "Romance", type="HAS_GENRE")

    # Relationships for The Matrix
    G.add_edge("Keanu Reeves", "The Matrix", type="ACTED_IN")
    G.add_edge("Lana Wachowski", "The Matrix", type="DIRECTED")
    G.add_edge("The Matrix", "Sci-Fi", type="HAS_GENRE")
    G.add_edge("The Matrix", "Action", type="HAS_GENRE")

    # Relationships for Interstellar
    G.add_edge("Christopher Nolan", "Interstellar", type="DIRECTED")
    G.add_edge("Interstellar", "Sci-Fi", type="HAS_GENRE")

    save_graph(G)
    return G
