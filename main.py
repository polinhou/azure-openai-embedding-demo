"""
Vector Search Demo with Qdrant and Azure OpenAI

This script demonstrates how to:
1. Generate text embeddings using Azure OpenAI
2. Index embeddings using Qdrant for efficient similarity search
3. Perform vector similarity search
"""

import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT").rstrip('/'),  # Remove trailing slash
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Add deployment name
)

# Get model name from environment variables
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")

# Initialize Qdrant client using environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "lyrics")

# Initialize Qdrant client
qdrant_client = QdrantClient(url=QDRANT_URL)

def get_embedding(text: str, model_name: str) -> List[float]:
    """
    Get embedding vector for the input text using Azure OpenAI.
    
    Args:
        text: Input text to generate embedding for
        model_name: Name of the Azure OpenAI model
        
    Returns:
        List of float numbers representing the embedding vector
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=model_name
        )

        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        raise

def setup_qdrant_collection(collection_name: str, vector_size: int, max_retries: int = 3) -> None:
    """
    Set up a Qdrant collection for storing embeddings.
    
    Args:
        collection_name: Name of the collection to create
        vector_size: Dimensionality of the embedding vectors
        max_retries: Maximum number of retry attempts for collection operations
    """
    import time
    from qdrant_client.http.exceptions import UnexpectedResponse, UnexpectedResponse
    from qdrant_client import QdrantClient
    
    for attempt in range(max_retries):
        try:
            # First, try to delete the collection if it exists
            try:
                collections = qdrant_client.get_collections()
                collection_names = [collection.name for collection in collections.collections]
                
                if collection_name in collection_names:
                    print(f"Deleting existing collection '{collection_name}' (attempt {attempt + 1}/{max_retries})...")
                    qdrant_client.delete_collection(collection_name)
                    # Give Qdrant more time to process the deletion
                    time.sleep(2)
            except Exception as e:
                print(f"Warning: Failed to check/delete collection: {str(e)}")
            
            # Then try to create the new collection
            print(f"Creating collection '{collection_name}' with vector size {vector_size}...")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={"text": models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )}
            )
            
            # Verify the collection was created
            collections = qdrant_client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            if collection_name in collection_names:
                print(f"Successfully created collection '{collection_name}'")
                return
            else:
                raise Exception(f"Failed to verify collection '{collection_name}' creation")
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to set up collection after {max_retries} attempts")
                print(f"Error details: {str(e)}")
                
                # Try to get more details about the error
                try:
                    collections = qdrant_client.get_collections()
                    print(f"Current collections: {[c.name for c in collections.collections]}")
                except Exception as e2:
                    print(f"Could not list collections: {str(e2)}")
                    
                # Try to force delete the collection data directory
                try:
                    print("Attempting to force cleanup...")
                    import shutil
                    import os
                    data_dir = os.path.join(os.getcwd(), 'qdrant_storage', 'collections', collection_name)
                    if os.path.exists(data_dir):
                        print(f"Removing collection data directory: {data_dir}")
                        shutil.rmtree(data_dir)
                        print("Data directory removed. Please restart the application.")
                except Exception as e2:
                    print(f"Failed to force cleanup: {str(e2)}")
                    
                raise
                
            print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)  # Exponential backoff

def add_to_qdrant(
    collection_name: str,
    data_objs: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> None:
    """
    Add lyrics and their embeddings to Qdrant.
    
    Args:
        collection_name: Name of the Qdrant collection
        data_objs: List of lyric objects with id and lyric text
        embeddings: List of corresponding embedding vectors
    """
    # Prepare points for Qdrant
    points = [
        models.PointStruct(
            id=idx,
            vector={"text": embedding},
            payload={"text": data_obj["lyric"], "id": data_obj["id"]}
        )
        for idx, (data_obj, embedding) in enumerate(zip(data_objs, embeddings))
    ]
    
    # Upload points to Qdrant
    operation_info = qdrant_client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )
    print(f"Uploaded {len(points)} points to collection '{collection_name}'")

def search_similar(
    collection_name: str,
    query_embedding: List[float],
    limit: int = 1
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors in Qdrant.
    
    Args:
        collection_name: Name of the Qdrant collection
        query_embedding: Query embedding vector
        limit: Maximum number of results to return
        
    Returns:
        List of search results with payload and score
    """
    from qdrant_client.http import models as rest
    
    # Search for similar vectors
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=("text", query_embedding),  # Specify vector name 'text'
        limit=limit,
        with_vectors=False,
        with_payload=True
    )
    
    results = []
    for hit in search_result:
        payload = hit.payload or {}
        results.append({
            "lyric": payload.get("text", ""),  
            "id": payload.get("id"),
            "score": hit.score
        })
    return results

def main() -> None:
    """Main function to demonstrate the embedding and search functionality."""
    # Example texts for demonstration
    data_objs = [
        {
            "id": 1,
            "lyric": "說了再見，才發現再也見不到"
        },
        {
            "id": 2,
            "lyric": "天涼了，雨下了，妳走了"
        }
    ]

    try:
        print("Generating embeddings...")
        # Generate embeddings for all lyrics
        texts = [item["lyric"] for item in data_objs]
        embedding_array = [get_embedding(text, MODEL_NAME) for text in texts]
        embedding_dim = len(embedding_array[0]) if embedding_array else 0
        
        print(f"Setting up Qdrant collection with {len(embedding_array)} vectors of dim {embedding_dim}...")
        # Set up Qdrant collection and add documents
        setup_qdrant_collection(COLLECTION_NAME, embedding_dim)
        add_to_qdrant(COLLECTION_NAME, data_objs, embedding_array)
        
        # Example search
        print("\nPerforming similarity search...")
        query_text = "我說再見"
        print(f"Query: {query_text}")
        query_embedding = get_embedding(query_text, MODEL_NAME)
        
        results = search_similar(COLLECTION_NAME, query_embedding, limit=2)  # Show top 2 results
        
        print("\nSearch Results:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"Result {i} (Score: {result['score']:.4f}):")
            print(f"ID: {result['id']}")
            print(f"Lyric: {result['lyric']}")
            print("-" * 80)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is running and the model is downloaded")
        print("2. Check your internet connection if using remote models")
        print(f"3. Verify the collection '{COLLECTION_NAME}' exists in Qdrant")


if __name__ == "__main__":
    main()
