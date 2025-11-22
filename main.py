import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore

# --- CONFIGURATION ---
PROJECT_ID = "dogwood-channel-478619-p7"
DATABASE_NAME = "mryash7878" 
REGION = "asia-south1"

# Initialize Clients
db = firestore.Client(project=PROJECT_ID, database=DATABASE_NAME)
vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel("gemini-2.5-flash")

# --- THE FUNCTION (Gen 1 Signature) ---
def firestore_reactor(data, context):
    """ Triggered by a change to a Firestore document.
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    # In Gen 1, 'data' is the dictionary automatically
    value = data.get("value")
    
    if not value:
        print("No value found in event.")
        return

    fields = value.get("fields", {})
    
    # Check if 'question' exists
    if "question" not in fields:
        print("No question field found.")
        return
    
    question_text = fields["question"]["stringValue"]
    
    # Get Document ID
    doc_path = value["name"]
    doc_id = doc_path.split("/")[-1]

    # Prevent infinite loops
    if "answer" in fields:
        print("Already answered. Skipping.")
        return

    print(f"🔔 New Question: {question_text}")

    # Ask AI
    try:
        response = model.generate_content(question_text)
        answer_text = response.text
    except Exception as e:
        answer_text = f"AI Error: {e}"

    # Write Back
    print("💾 Saving answer...")
    doc_ref = db.collection("chatbot").document(doc_id)
    doc_ref.update({"answer": answer_text, "status": "cloud_handled"})
    print("✅ Done!")
