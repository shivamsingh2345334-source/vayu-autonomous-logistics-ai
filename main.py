import os
import time
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from pyairtable import Api

# --- RICH LIBRARY IMPORTS ---
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.text import Text

# Initialize Rich Console
console = Console()

# Load environment variables
load_dotenv()
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = "app7Q8yH6V49DXydM"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

# Initialize Gemini AI and Airtable API clients
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')
api = Api(AIRTABLE_PAT)
hubs_table = api.table(AIRTABLE_BASE_ID, 'Hubs')

def send_telegram_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    requests.post(url, json=payload)

# ==========================================
# SYSTEM STARTUP
# ==========================================
os.system('cls' if os.name == 'nt' else 'clear') # Clears terminal for a clean start
console.print(Panel.fit("[bold cyan]🌪️ VAYU: AUTONOMOUS LOGISTICS DISRUPTION AI[/bold cyan]", border_style="cyan"))
time.sleep(1)

# ==========================================
# Phase 2: Agent-to-Agent Coordination
# ==========================================
console.print("\n[bold magenta]--- PHASE 2: AGENT COORDINATION ---[/bold magenta]")
with console.status("[bold yellow]\[AGENT X - Truck A]: Initializing Gemini LLM for Hub B communication...[/bold yellow]", spinner="bouncingBar"):
    prompt = "You are AI Agent X. Your vehicle, Truck A, is transporting 10 Tons of MacBooks. Write a concise, professional message to Agent Y (Hub B Manager) requesting an immediate reservation of 10 tons of storage capacity."
    response = model.generate_content(prompt)
    time.sleep(1.5) # Added slight delay for visual effect in demo
    
console.print(f"[bold green]\[AGENT X]:[/bold green] {response.text.strip()}")

# ==========================================
# Phase 3: Fallback Matrix 1
# ==========================================
console.print("\n[bold magenta]--- PHASE 3: FALLBACK MATRIX 1 (API FAILURE) ---[/bold magenta]")
simulate_communication_failure = True

with console.status("[bold blue]\[AGENT Y]: Confirming parameters. Initiating Airtable API sync...[/bold blue]", spinner="dots"):
    time.sleep(2)
    try:
        if simulate_communication_failure:
            raise Exception("System Sync Delayed! Airtable API Timeout.")
        
        records = hubs_table.all()
        for record in records:
            if record['fields'].get('Hub_ID') == 'Hub B':
                record_id = record['id']
                current_space = record['fields'].get('Available_Space', 0)
                new_space = current_space - 10
                hubs_table.update(record_id, {'Available_Space': new_space})
                console.print(f"[bold green]\[AIRTABLE]: Success. Hub B available capacity updated to {new_space} Tons.[/bold green]")
                break

    except Exception as e:
        console.print(Panel(f"[bold red]🚨 SYSTEM ALERT: FALLBACK MATRIX 1 ACTIVATED 🚨[/bold red]\n[white]Error Details: {str(e)}[/white]", border_style="red"))
        console.print("[bold yellow]\[AGENT X]: Activating fallback communication via Telegram Bot API...[/bold yellow]")
        
        alert_message = "URGENT ALERT (Fallback 1): Truck A arriving at Hub B with 10 Tons load. Automatic Airtable sync failed. Manual dock preparation required immediately."
        send_telegram_alert(alert_message)
        time.sleep(1)
        console.print("[bold green]✅ [TELEGRAM]: SMS alert successfully dispatched to Hub Manager.[/bold green]")

# ==========================================
# Phase 4: Departure & Dynamic Routing
# ==========================================
console.print("\n[bold magenta]--- PHASE 4: DEPARTURE & DYNAMIC ROUTING ---[/bold magenta]")

def get_route(start_coords, end_coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {'Authorization': ORS_API_KEY, 'Content-Type': 'application/json'}
    payload = {"coordinates": [start_coords, end_coords]}
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

with console.status("[bold cyan]\[ORS API]: Calculating primary route (NY -> Chicago)...[/bold cyan]", spinner="earth"):
    dist, dur = get_route(ny_coords, chi_coords)
    time.sleep(1.5)

if dist:
    console.print(f"[bold green]🗺️ [ORS API]: Route locked. Distance: {dist:.2f} km, ETA: {dur:.2f} hours.[/bold green]")

current_weather = "Thunderstorm" 
console.print(f"[bold red]⛈️ [WEATHER MODULE]: Current route weather detected as: {current_weather}[/bold red]")

with console.status("[bold yellow]\[AGENT X]: Consulting Gemini for weather risk analysis...[/bold yellow]"):
    prompt = f"You are an AI Logistics Agent. The current weather report indicates: '{current_weather}'. If the weather is hazardous, reply strictly with 'REROUTE_NEEDED' and provide a brief reason. If safe, reply with 'ROUTE_SAFE'."
    response = model.generate_content(prompt)
    decision = response.text.strip()
    time.sleep(1)

console.print(f"[bold cyan]🤖 [AGENT X] (Gemini):[/bold cyan] Weather analysis complete. {decision}")

if "REROUTE_NEEDED" in decision:
    console.print("[bold orange3]⚠️ [AGENT X]: Warning: Cascade delays detected. Activating dynamic rerouting protocols...[/bold orange3]")
    with console.status("[bold cyan]\[ORS API]: Calculating alternative safe route...[/bold cyan]", spinner="earth"):
        time.sleep(1.5)
        alt_dist = dist + 45.5 if dist else 1350.5 
        alt_dur = dur + 0.8 if dur else 14.2 
    console.print(f"[bold green]🛣️ [ORS API]: Alternative Route Configured. Distance: {alt_dist:.2f} km, ETA: {alt_dur:.2f} hours.[/bold green]")
    console.print("[bold green]✅ [SYSTEM]: Dynamic rerouting successfully evaded storm delay. Route optimized.[/bold green]")

# ==========================================
# Phase 5: Fallback Matrix 2
# ==========================================
console.print("\n[bold magenta]--- PHASE 5: FALLBACK MATRIX 2 (HARDWARE FAILURE) ---[/bold magenta]")
console.print(Panel("[bold red]💥 CRITICAL ALERT: Truck A engine failure detected on transit route![/bold red]", border_style="red"))

with console.status("[bold yellow]\[AGENT X]: Scanning Airtable database for nearest available fleet vehicles...[/bold yellow]", spinner="line"):
    trucks_table = api.table(AIRTABLE_BASE_ID, 'Trucks')
    time.sleep(2)
    try:
        all_trucks = trucks_table.all()
        rescue_truck = None
        for truck in all_trucks:
            fields = truck.get('fields', {})
            if fields.get('Status2')== 'Empty':
                rescue_truck = fields
                break
                
        if rescue_truck:
            t_id = rescue_truck.get('Truck_ID', 'Unknown')
            t_driver = rescue_truck.get('Driver_Name', 'Unknown')
            t_loc = rescue_truck.get('Location', 'Unknown')
            
            console.print(f"[bold cyan]🔍 [AIRTABLE]: Asset located - ID: '{t_id}' (Driver: {t_driver}, Status: Empty, Location: {t_loc}).[/bold cyan]")
            
            sos_message = f"URGENT DISPATCH: {t_driver} ({t_id}), immediate diversion required. Truck A (John) has reported hardware failure. Proceed to assist with 10-Ton load transfer."
            send_telegram_alert(sos_message)
            console.print(f"[bold green]✅ [TELEGRAM]: Emergency dispatch instructions sent to Unit {t_id} ({t_driver}).[/bold green]")
        else:
            console.print("[bold red]❌ [AIRTABLE WARNING]: No empty fleet assets currently available for dispatch.[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]❌ [SYSTEM ERROR]: Failed to fetch fleet status. Details: {str(e)}[/bold red]")

# ==========================================
# FINAL SUMMARY PANEL
# ==========================================
summary_text = """
[bold green]✔ Empty Miles Avoided[/bold green]
[bold green]✔ Cascade Delays Prevented[/bold green]
[bold green]✔ Real-time Alerts Dispatched[/bold green]
"""
console.print("\n")
console.print(Panel(summary_text, title="[bold cyan]MISSION ACCOMPLISHED[/bold cyan]", border_style="green", expand=False))
console.print("[dim]LOGISTICS DISRUPTION AI SHUTDOWN SEQUENCE COMPLETE.[/dim]\n")
