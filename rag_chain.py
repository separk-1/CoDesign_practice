import networkx as nx
from typing import Optional
import re

def execute_rag_chain(graph, query: str, client, model: str):
    # Retrieve relevant subgraph based on the query
    sub = retrieve(graph, query)
    context = format_subgraph_for_prompt(sub)

    # Simple prompt for the LLM
    prompt = f"""You are a helpful assistant.
Use ONLY the context below. If you don't know, say so.

[CONTEXT]
{context}

[QUESTION]
{query}
"""

    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = r.choices[0].message.content or ""

    return {
        "reply": answer,
        "context": context,  # Return context for educational purposes
    }


def retrieve(graph: nx.Graph, query: str) -> Optional[nx.Graph]:
    """
    Keyword-based retrieval.
    Finds nodes where:
    1. The node ID is part of the query (e.g., query "Apple" matches node "Apple").
    2. Any significant keyword (len > 2) from the query appears in the node ID or attributes.
    """
    query_lower = query.lower()

    # Extract significant keywords (length > 2) using regex to handle punctuation
    query_tokens = {word for word in re.findall(r'\w+', query_lower) if len(word) > 2}

    relevant_nodes = set()

    for node_id, data in graph.nodes(data=True):
        node_id_str = str(node_id).lower()

        # 1. Exact or partial match of Node ID in Query
        # e.g., Node "Apple", Query "Tell me about Apple" -> Match
        if node_id_str in query_lower:
            relevant_nodes.add(node_id)
            continue

        # 2. Keyword overlap
        # Check if any query token appears in Node ID or Attributes
        # e.g., Query "red fruit", Node Attribute "Color: Red" -> Match ("red" in "red")

        # Combine all node text into one string for checking
        node_text = node_id_str + " " + " ".join(str(v).lower() for v in data.values())

        if any(token in node_text for token in query_tokens):
            relevant_nodes.add(node_id)
            continue

    if not relevant_nodes:
        return None

    # Include neighbors of relevant nodes to provide context
    subgraph_nodes = set(relevant_nodes)
    for node_id in relevant_nodes:
        # Handle both directed and undirected graphs
        if isinstance(graph, nx.DiGraph):
             neighbors = list(graph.successors(node_id)) + list(graph.predecessors(node_id))
        else:
             neighbors = list(graph.neighbors(node_id))

        for n in neighbors:
            subgraph_nodes.add(n)

    return graph.subgraph(subgraph_nodes)


def format_subgraph_for_prompt(subgraph, max_nodes=15, max_edges=30):
    if not subgraph:
        return "No relevant information found in the knowledge graph."

    nodes = list(subgraph.nodes(data=True))[:max_nodes]
    # Keep track of nodes included to filter edges
    node_ids = {nid for nid, _ in nodes}

    edges = [
        (s, t, d) for s, t, d in subgraph.edges(data=True)
        if s in node_ids and t in node_ids
    ][:max_edges]

    lines = ["Here is the relevant information from the knowledge graph:"]

    # Format nodes
    for nid, data in nodes:
        node_info = f"- Node: {nid}"
        attrs = []
        for k, v in data.items():
            # Skip internal keys if any (none in this simple example, but good practice)
            attrs.append(f"{k}: {v}")

        if attrs:
            node_info += f" ({', '.join(attrs)})"
        lines.append(node_info)

    lines.append("\nRelationships:")
    # Format edges
    for s, t, d in edges:
        rel_type = d.get("type", "related_to")
        lines.append(f"- {s} --[{rel_type}]--> {t}")

    return "\n".join(lines)
