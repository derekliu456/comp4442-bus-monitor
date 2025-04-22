import os, json, datetime, requests

RAW_DIR = "scraper/data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

ROUTES = ["1A","104","170"]
BASE = "https://data.etabus.gov.hk/v1/transport/kmb"

def fetch_and_store():
    now = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for route in ROUTES:
        stops = requests.get(f"{BASE}/route-stop/{route}/inbound/1").json().get("data", [])
        for s in stops[:5]:
            stop_id = s["stop"]
            data = requests.get(f"{BASE}/eta/{route}/{stop_id}/inbound/1").json()
            fname = f"{now}_{route}_{stop_id}.json"
            with open(os.path.join(RAW_DIR, fname),"w") as f:
                json.dump(data, f)

if __name__=="__main__":
    fetch_and_store()
