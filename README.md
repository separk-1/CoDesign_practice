# GraphRAG Practice

This is a simple GraphRAG (Graph Retrieval-Augmented Generation) practice project.
It demonstrates how to retrieve information from a Knowledge Graph and use it with an LLM (Language Model) to answer questions.

## 1. Setup

First, you need to set up your environment using Conda.

### Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
conda create -n myenv python=3.11 -y
conda activate myenv
```

### Install Dependencies
Install the required libraries using `pip`.

```bash
pip install -r requirements.txt
```

### Set API Key
You need an OpenAI API Key to run this project.
Create a file named `.env` in the root folder and add your key:

```
OPENAI_API_KEY=sk-proj-xxxx...
```

*(You can copy `.env.example` if it exists, but creating a new file is fine too.)*

## 2. Run the App

Start the web server with the following command:

```bash
python app.py
```

After the server starts, open your browser and go to:
[http://localhost:5001](http://localhost:5001)

## 3. How to Use

1. **View Knowledge Graph**: Click the button to visualize the nodes and edges in the graph (e.g., Inception, Titanic, Sci-Fi).
2. **Ask a Question**: Type a question like "Who directed Inception?" or "Tell me about Sci-Fi movies."
3. **See the Result**: The app will search the graph for relevant information and use the LLM to generate an answer.

### Sample Queries
You can find more example queries in `queries.json`. Try these to explore different relationships:

- **Direct Retrieval:** "What is Inception?"
- **Relationships:** "Which movies did Leonardo DiCaprio act in?"
- **Multi-hop:** "Are there any movies directed by Christopher Nolan that are also Sci-Fi?"
- **Thematic:** "Find movies about dreams or reality simulations."

## 4. Explore the Code

- **`knowledge_graph.json`**: This file stores the graph data (nodes and links).
- **`queries.json`**: Contains a list of sample questions to practice with.
- **`rag_chain.py`**: This file contains the logic for retrieving relevant nodes and sending the prompt to the LLM.
- **`graph_manager.py`**: Helper functions to load and save the graph.
- **`app.py`**: The web server API.
