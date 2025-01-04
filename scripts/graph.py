import networkx as nx
import numpy as np
import pickle

helper_path = "../data/helperData4"  # Metadata storage path

def build_knowledge_graph():
    """
    Build a knowledge graph from the metadata stored during vector store creation.

    Returns:
    - graph (networkx.Graph): The knowledge graph.
    """
    graph = nx.Graph()

    # Load metadata
    metadata_list = np.load(f"{helper_path}/metadata.npy", allow_pickle=True)

    # Add relationships (this is an example, adjust based on your use case)
    for idx, metadata in enumerate(metadata_list):
        current_id = metadata['id']
        current_chapter = metadata['chapter']
        current_verse = metadata['verse']
        
        # Sequential relationship (next verse)
        if idx < len(metadata_list) - 1:
            next_metadata = metadata_list[idx + 1]
            if next_metadata['chapter'] == current_chapter:
                graph.add_edge(
                    current_id, 
                    next_metadata['id'], 
                    relation="next"
                )
        
        # Related by theme (e.g., similar purport or translations)
        for other_metadata in metadata_list:
            if metadata['id'] != other_metadata['id'] and \
               set(metadata['translations']) & set(other_metadata['translations']):
                graph.add_edge(
                    current_id, 
                    other_metadata['id'], 
                    relation="related_theme"
                )
    
    return graph

def save_graph(graph, path="../data/graphs/knowledge_graph.pkl"):
    with open(path, "wb") as f:
        pickle.dump(graph, f)
    print("Knowledge graph saved.")

if __name__ == "__main__":
    graph = build_knowledge_graph()
    save_graph(graph)