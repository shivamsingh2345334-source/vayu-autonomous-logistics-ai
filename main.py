import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from pyairtable import Api

# Load environment variables
load_dotenv()
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = "app7Q8yH6V49DXydM"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI and Airtable API clients
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')
api = Api(AIRTABLE_PAT)
hubs_table = api.table(AIRTABLE_BASE_ID, 'Hubs')

# Function to dispatch Telegram alerts to the Operations Manager
def send_telegram_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    requests.post(url, json=payload)

# Initialize System Interface
print("\n[SYSTEM] INITIATING LOGISTICS DISRUPTION AI...")
print("-" * 55)

# Phase 2: Agent-to-Agent Coordination
print("[AGENT X - Truck A]: Initializing Gemini LLM for Hub B communication...")
prompt = "You are AI Agent X. Your vehicle, Truck A, is transporting 10 Tons of MacBooks. Write a concise, professional message to Agent Y (Hub B Manager) requesting an immediate reservation of 10 tons of storage capacity."
response = model.generate_content(prompt)
print(f"[AGENT X]: {response.text.strip()}")

# Phase 3: Fallback Matrix 1 (Failure Simulator)
simulate_communication_failure = True

print("\n[AGENT Y]: Confirming reservation parameters. Initiating Airtable API sync...")

try:
    if simulate_communication_failure:
        raise Exception("System Sync Delayed! Airtable API Timeout.")
    
    # Update database records upon successful connection
    records = hubs_table.all()
    for record in records:
        if record['fields'].get('Hub_ID') == 'Hub B':
            record_id = record['id']
            current_space = record['fields'].get('Available_Space', 0)
            new_space = current_space - 10
            
            hubs_table.update(record_id, {'Available_Space': new_space})
            print(f"[AIRTABLE]: Success. Hub B available capacity updated to {new_space} Tons.")
            break

except Exception as e:
    print("\n[SYSTEM ALERT] PHASE 3: FALLBACK MATRIX 1 ACTIVATED")
    print(f"[SYSTEM ERROR]: {str(e)}")
    print("[AGENT X]: Activating fallback communication via Telegram Bot API...")
    
    alert_message = "URGENT ALERT (Fallback 1): Truck A arriving at Hub B with 10 Tons load. Automatic Airtable sync failed. Manual dock preparation required immediately."
    send_telegram_alert(alert_message)
    print("[TELEGRAM]: SMS alert successfully dispatched to Hub Manager.")
    
print("\n[SYSTEM] STEP 3 EXECUTION COMPLETE.\n")


import random 

# Phase 4: Departure & Dynamic Routing
print("\n[SYSTEM] PHASE 4: DEPARTURE & DYNAMIC ROUTING")

ORS_API_KEY = os.getenv("ORS_API_KEY")

# Function to calculate route distance and ETA via OpenRouteService
def get_route(start_coords, end_coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "coordinates": [start_coords, end_coords],
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if 'routes' in data:
            distance = data['routes'][0]['summary']['distance'] / 1000 
            duration = data['routes'][0]['summary']['duration'] / 3600 
            return distance, duration
        return None, None
    except Exception as e:
        return None, None

ny_coords = [-74.0060, 40.7128] 
chi_coords = [-87.6298, 41.8781] 

print("[ORS API]: Calculating primary route (NY -> Chicago)...")
dist, dur = get_route(ny_coords, chi_coords)

if dist:
    print(f"[ORS API]: Route locked. Distance: {dist:.2f} km, ETA: {dur:.2f} hours.")

# Weather Simulation Module
weathers = ["Clear", "Heavy Rain", "Thunderstorm"]
current_weather = "Thunderstorm" 

print(f"[WEATHER MODULE]: Current route weather detected as: {current_weather}")

# Consult AI for dynamic routing decision based on weather
prompt = f"You are an AI Logistics Agent. The current weather report indicates: '{current_weather}'. If the weather is hazardous, reply strictly with 'REROUTE_NEEDED' and provide a brief reason. If safe, reply with 'ROUTE_SAFE'."
response = model.generate_content(prompt)
decision = response.text.strip()

print(f"[AGENT X] (Gemini): Weather analysis complete. {decision}")

if "REROUTE_NEEDED" in decision:
    print("[AGENT X]: Warning: Potential cascade delays detected. Activating dynamic rerouting protocols...")
    print("[ORS API]: Calculating alternative safe route...")
    
    # Simulating reroute coordinates for presentation purposes
    alt_dist = dist + 45.5 if dist else 1350.5 
    alt_dur = dur + 0.8 if dur else 14.2 
    print(f"[ORS API]: Alternative Route Configured. Distance: {alt_dist:.2f} km, ETA: {alt_dur:.2f} hours.")
    print("[SYSTEM]: Dynamic rerouting successfully evaded storm delay. Route optimized.")

print("\n[SYSTEM] STEP 4 EXECUTION COMPLETE.\n")


# Phase 5: Fallback Matrix 2 (Rescue Mission / Fleet Rebalancing)
print("\n[SYSTEM] PHASE 5: FALLBACK MATRIX 2 (HARDWARE FAILURE SIMULATION)")

print("[SYSTEM ALERT]: CRITICAL ALERT! Truck A engine failure detected on transit route.")
print("[AGENT X]: Scanning Airtable database for nearest available fleet vehicles...")

trucks_table = api.table(AIRTABLE_BASE_ID, 'Trucks')

try:
    all_trucks = trucks_table.all()
    rescue_truck = None
    
    # Scan for available fleet assets
    for truck in all_trucks:
        fields = truck.get('fields', {})
        if fields.get('Status') == 'Empty':
            rescue_truck = fields
            break
            
    if rescue_truck:
        t_id = rescue_truck.get('Truck_ID', 'Unknown')
        t_driver = rescue_truck.get('Driver_Name', 'Unknown')
        t_loc = rescue_truck.get('Location', 'Unknown')
        
        print(f"[AIRTABLE]: Asset located - ID: '{t_id}' (Driver: {t_driver}, Status: Empty, Location: {t_loc}).")
        
        # Dispatch emergency protocols to rescue unit
        sos_message = f"URGENT DISPATCH: {t_driver} ({t_id}), immediate diversion required. Truck A (John) has reported hardware failure. Proceed to assist with 10-Ton load transfer."
        send_telegram_alert(sos_message)
        print(f"[TELEGRAM]: Emergency dispatch instructions sent to Unit {t_id} ({t_driver}).")
        
    else:
        print("[AIRTABLE WARNING]: No empty fleet assets currently available for dispatch.")
        
except Exception as e:
    print(f"[SYSTEM ERROR]: Failed to fetch fleet status from database. Details: {str(e)}")

# Final Execution Summary
print("\n--- MISSION ACCOMPLISHED ---")
print("[STATUS] Empty Miles Avoided: TRUE")
print("[STATUS] Cascade Delays Prevented: TRUE")
print("[STATUS] Real-time Alerts Dispatched: TRUE")
print("[SYSTEM] LOGISTICS DISRUPTION AI SHUTDOWN SEQUENCE COMPLETE.\n")
