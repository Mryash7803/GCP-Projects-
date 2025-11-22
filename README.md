
## 📖 Overview
This project implements a **Serverless Event-Driven Architecture** using Google Cloud Platform (GCP). It acts as an intelligent backend for a chatbot application.

Instead of running a 24/7 server, this system utilizes **Cloud Functions** to "scale to zero," meaning it costs nothing when idle. It listens to a **NoSQL Database (Firestore)** in real-time; when a user posts a question, the system automatically wakes up, consults Google's **Gemini AI**, and writes the answer back to the database.

## 🏗️ Architecture

The system follows a strictly decoupled, event-driven pattern:

```mermaid
graph LR
    A[User] -- Writes Question --> B((Firestore DB))
    B -- Trigger Event --> C[Cloud Function]
    C -- API Call --> D[Vertex AI Gemini]
    D -- Response --> C
    C -- Write Answer --> B
Trigger: A new document is added to the chatbot collection in Firestore.

Compute: Google Cloud Functions (Gen 1) triggers instantly on the document.write event.

Intelligence: Vertex AI (Gemini 2.5 Flash) generates a context-aware response.

Persistence: The function updates the original Firestore document with the answer and a completion status.

🛠️ Tech Stack
Cloud Provider: Google Cloud Platform (GCP)

Region: asia-south1 (Mumbai)

Compute: Cloud Functions (Python 3.11)

Database: Cloud Firestore (Native Mode)

AI Model: Gemini 2.5 Flash (via Vertex AI SDK)

Infrastructure: Deployed via Google Cloud SDK (gcloud CLI)

💻 The Code Logic (main.py)
The core logic handles the database trigger, sanitizes input, and manages the AI interaction.

Python

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore

# Configuration
PROJECT_ID = "YOUR_PROJECT_ID"
DATABASE_NAME = "YOUR_DB_NAME" 
REGION = "asia-south1"

# Initialize Clients
db = firestore.Client(project=PROJECT_ID, database=DATABASE_NAME)
vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel("gemini-2.5-flash")

def firestore_reactor(data, context):
    """ Triggered by a change to a Firestore document. """
    
    # Parse Event Data
    value = data.get("value")
    fields = value.get("fields", {})
    
    if "question" not in fields:
        return
    
    question_text = fields["question"]["stringValue"]
    doc_path = value["name"]
    doc_id = doc_path.split("/")[-1]

    # Prevent Infinite Loops
    if "answer" in fields:
        print("Already answered. Skipping.")
        return

    print(f"🔔 New Question: {question_text}")

    # Generate AI Response
    try:
        response = model.generate_content(question_text)
        answer_text = response.text
    except Exception as e:
        answer_text = f"AI Error: {e}"

    # Write Back to Database
    doc_ref = db.collection("chatbot").document(doc_id)
    doc_ref.update({"answer": answer_text, "status": "cloud_handled"})
    print("✅ Done!")
🚀 Deployment Steps
1. Prerequisites
Google Cloud Project with Billing enabled.

APIs Enabled: Cloud Functions, Firestore, Vertex AI, Cloud Build.

2. Create the Database
Ensure a Firestore database is created in Native Mode. Note the database name (e.g., (default) or a custom name).

3. Deploy Command
This project uses Generation 1 Cloud Functions to ensure a direct, unfiltered connection to named databases.

Bash

gcloud functions deploy my-ai-bot-v1 \
--region=asia-south1 \
--entry-point=firestore_reactor \
--runtime=python311 \
--source=. \
--memory=512MB \
--trigger-event=providers/cloud.firestore/eventTypes/document.write \
--trigger-resource="projects/YOUR_PROJECT_ID/databases/YOUR_DB_NAME/documents/chatbot/{docId}" \
--no-gen2
🧪 How to Test
Go to the Google Cloud Console -> Firestore.

Navigate to the chatbot collection.

Add a Document:

Field: question

Value: "What is the speed of light?"

Refresh the page after 2-3 seconds.

You will see a new field answer populated automatically by the Cloud Function.
