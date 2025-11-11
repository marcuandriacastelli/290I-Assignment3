from fastapi import FastAPI, File, UploadFile, HTTPException
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Reçoit ton fichier JSON, construit le graphe,
    et le garde en mémoire pour la suite.
    """
    global active_graph
    try:
        # utilitaire fourni dans utils.py
        active_graph = create_graph_from_json(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON or cannot build graph: {e}")

    return {
        "status": "ok",
        "message": "Graph uploaded and ready!",
        "node_count": len(active_graph.nodes),
        "nodes": list(active_graph.nodes.keys()),
    }



@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    """
    Calcule le plus court chemin entre start et end
    avec Dijkstra, puis renvoie la route et la distance.
    """
    global active_graph
    if active_graph is None:
        raise HTTPException(status_code=400, detail="No graph yet. Upload a JSON at /upload_graph_json/ first.")

    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        raise HTTPException(status_code=404, detail="Start or end node does not exist in the current graph.")

    # 1) Lancer Dijkstra depuis le start
    start_node = active_graph.nodes[start_node_id]
    dijkstra(active_graph, start_node)

    # 2) Récupérer l’info au end
    end_node = active_graph.nodes[end_node_id]

    import math
    if math.isinf(float(end_node.dist)):
        raise HTTPException(status_code=400, detail=f"No path from {start_node_id} to {end_node_id}.")

    # 3) Reconstruire le chemin en remontant prev
    path = []
    cur = end_node
    while cur is not None:
        path.append(cur.id)
        cur = cur.prev
    path.reverse()

    return {
        "status": "ok",
        "path": path,
        "total_distance": float(end_node.dist),
    }


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    