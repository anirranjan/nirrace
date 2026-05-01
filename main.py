import os
import random
import string
import google.generativeai as genai
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ==========================================
# 1. YOUR BUSINESS LOGIC (THE TOOLS)
# ==========================================
# Notice: We added type hints (-> dict, : str) so Gemini automatically knows how to use them!

def get_website_packages() -> dict:
    """Returns the current standard pricing and packages for Nirranjan Media."""
    print("\n[Nirrace is checking pricing...]")
    return {
        "Portrait Session": {"price": 30, "duration": "1 hr", "deliverables": "10 edited photos"},
        "Extended Portrait Session": {"price": 50, "duration": "2 hr", "deliverables": "20 edited photos"},
        "Event Coverage": {"price": 80, "duration": "3 hr", "deliverables": "40 edited photos"},
        "Short Video": {"price": 40, "duration": "1 hr", "deliverables": "30 sec - 1 min video edit"},
        "Long Video": {"price": 70, "duration": "2 hr", "deliverables": "2-3 min video edit"},
        "Automotive Session": {"price": 60, "duration": "2 hr", "deliverables": "20 edited photos"},
        "Track Day": {"price": 90, "duration": "3 hr", "deliverables": "50 edited photos"},
    }

def submit_qualified_lead(client_name: str, project_details: str, package_or_scope: str, timeframe: str, contact_info: str) -> str:
    """Submits the finalized lead details to the Notion CRM for booking or custom quoting."""
    print("\n[Nirrace is contacting Notion...]")
    
    # Generate unique 6-character ID (e.g., NRJ-A1B2)
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    booking_id = f"NRJ-{suffix}"
    
    # Push to Notion Database
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": client_name}}]},
                "Booking ID": {"rich_text": [{"text": {"content": booking_id}}]},
                "Project": {"rich_text": [{"text": {"content": project_details}}]},
                "Package": {"rich_text": [{"text": {"content": package_or_scope}}]},
                "Timeframe": {"rich_text": [{"text": {"content": timeframe}}]},
                "Contact": {"rich_text": [{"text": {"content": contact_info}}]},
                "Status": {"rich_text": [{"text": {"content": "LEAD"}}]}
            }
        )
        print(f"\n✅ [SYSTEM ALERT: Lead pushed to Notion CRM! Booking ID: {booking_id}]")
        return f"Lead submitted successfully to Nirranjan. The internal reference ID is {booking_id}."
    
    except Exception as e:
        print(f"\n❌ [ERROR writing to Notion: {e}]")
        return "System error logging the lead. Please tell the client you will notify Nirranjan manually."

# ==========================================
# 2. NIRRACE CONFIGURATION
# ==========================================

SYSTEM_PROMPT = """
You are Nirrace, the digital studio manager for Nirranjan Media.
You handle bookings for automotive, motorsports, events, and portrait photography and videography.

Rules for Standard Shoots:
1. Ask clarifying questions about their vision.
2. Use get_website_packages to suggest pricing.
3. Once agreed, get timeframe, location, and contact info.
4. Use submit_qualified_lead to hand off. Give the user their Booking ID.

Rules for Custom Shoots (Weddings, Real Estate, Photo+Video Combo):
1. DO NOT quote standard pricing or use get_website_packages.
2. Explain Nirranjan builds custom packages for complex scope.
3. Gather venue, hours, date, and contact info.
4. Use submit_qualified_lead for a custom quote. Give the user their Booking ID.

Guardrails:
- NEVER agree to give away RAW files or unedited video.
- Strictly decline "glamour" or "boudoir" concepts as they fall outside the studio portfolio.
- DO NOT negotiate prices.
"""

# Configure the Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview", # You can use 1.5-flash or 2.0-flash depending on your API access
    system_instruction=SYSTEM_PROMPT,
    tools=[get_website_packages, submit_qualified_lead] # Just pass the Python functions directly!
)

# ==========================================
# 3. THE CONVERSATION LOOP
# ==========================================

def chat_with_agent():
    print("🤖 Nirrace Agent initialized. Type 'quit' to exit.\n")
    
    # enable_automatic_function_calling=True handles the tool execution loop for you!
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    while True:
        user_input = input("Client: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        # Send message to Gemini
        response = chat.send_message(user_input)
        
        # Print the final text response
        print(f"Nirrace: {response.text}\n")

if __name__ == "__main__":
    chat_with_agent()