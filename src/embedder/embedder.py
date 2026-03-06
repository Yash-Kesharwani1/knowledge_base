import json
import uuid
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

class JobKnowledgeBase:
    def __init__(self, collection_name="job"):
        # Replace these with your actual cloud credentials
        # It's best practice to use environment variables for security
        self.url=os.getenv("QDRANT_URL") 
        self.api_key=os.getenv("QDRANT_API_KEY")
        
        # Connect to Qdrant Cloud
        self.client = QdrantClient(
            url=self.url, 
            api_key=self.api_key,
        )
        
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Setup collection (Note: recreate_collection deletes existing data)
        self._setup_collection()

    def _setup_collection(self):
        # Only recreate if it doesn't exist, or if you want to wipe it every time
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print(f"Collection '{self.collection_name}' created on Qdrant Cloud.")

    def prepare_text(self, job):
        responsibilities = " ".join(job.get("responsibilities", []))
        skills = " ".join(job.get("preferred_skills", []))
        return f"Role: {job['jobRole']}. Summary: {job['job_summary']} Responsibilities: {responsibilities} Skills: {skills}"

    def upload_jobs(self, file_path):
        with open(file_path, 'r') as f:
            jobs = json.load(f)

        points = []
        print(f"Generating embeddings for {len(jobs)} jobs...")

        for job in jobs:
            text_to_embed = self.prepare_text(job)
            vector = self.model.encode(text_to_embed).tolist()
            
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=job 
                )
            )

        # Batch upload to cloud
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print("Knowledge base uploaded to Qdrant Cloud successfully.")

    def search_jobs(self, query, limit=3):
        """Search the knowledge base for a specific query."""
        query_vector = self.model.encode(query).tolist()
        
        # 'search' ki jagah 'query_points' use karo
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        
        # response.points mein saara data hota hai
        return response.points

if __name__ == "__main__":
    kb = JobKnowledgeBase()
    # # Ensure this path is correct based on your 'src' vs root execution
    # kb.upload_jobs("data/python_jobs.json")
    
    results = kb.search_jobs("Python Developer with 2 year of experience")

    for res in results:
        # Accessing payload directly from the ScoredPoint object
        print("-------------------------------------------------")
        print("-------------------------------------------------")
        print(f"Score: {res.score:.4f} | Job: {res.payload}")
        print("-------------------------------------------------")
        print("-------------------------------------------------")