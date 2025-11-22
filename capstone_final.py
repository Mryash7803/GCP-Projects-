import time
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore
from google.oauth2 import service_account

# ==========================================
# ⚙️ CONFIGURATION (ALL MUMBAI NOW 🇮��)
# ==========================================
PROJECT_ID = "dogwood-channel-478619-p7"

# If you just clicked "Create Database", the name is usually "(default)"
# If you named it something else (like "mryash-db"), change this line!
DATABASE_NAME = "mryash7878"

# Region: Mumbai
REGION = "asia-south1"

# Security: Your renamed key file
KEY_PATH = "/mnt/c/Users/yashs/Downloads/key.json"
# ==========================================

print("🚀 STARTING MUMBAI CAPSTONE SYSTEM...")

try:
    print("�� Loading Credentials...")
    creds = service_account.Credentials.from_service_account_file(KEY_PATH)
    
    print(f"🔌 Connecting to Firestore (Database: {DATABASE_NAME})...")
    db = firestore.Client(credentials=creds, project=PROJECT_ID, database=DATABASE_NAME)
    
    print(f"🔌 Connecting to Vertex AI (Brain: {REGION})...")
    vertexai.init(project=PROJECT_ID, location=REGION, credentials=creds)
    
    # Using the '001' version which is rock-stable in Mumbai
    model = GenerativeModel("gemini-2.5-flash")
    
    print("✅ System Online & Ready.")

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
    print("👉 Tip: If Error is 'Not Found', check if DATABASE_NAME is correct in the console.")
    exit()

# --- FUNCTION: ASK THE BOT ---
def ask_the_bot(question):
    print(f"🧠 AI is thinking about: '{question}'...")
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# --- FUNCTION: THE WATCHER ---
def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
            doc_id = change.document.id
            
            # Check if it's a question needing an answer
            if "question" in data and "answer" not in data:
                print(f"\n🔔 NEW QUESTION DETECTED: {data['question']}")
                
                # 1. Ask AI
                answer_text = ask_the_bot(data['question'])
                
                # 2. Save to DB
                print("💾 Saving answer to database...")
                db.collection("chatbot").document(doc_id).update({
                    "answer": answer_text,
                    "status": "completed",
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                print("✅ Cycle Complete. Waiting for next question.\n")

# --- RUN LOOP ---
print("👀 Monitoring 'chatbot' collection for new questions...")
# Create the reference to the collection
doc_ref = db.collection("chatbot")
# Start watching
query_watch = doc_ref.on_snapshot(on_snapshot)

while True:
    time.sleep(1)
