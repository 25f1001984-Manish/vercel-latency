from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os

app = FastAPI()

def get_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
    with open(data_path) as f:
        return json.load(f)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}

@app.options("/{rest_of_path:path}")
async def preflight(rest_of_path: str):
    return JSONResponse(content={}, headers=CORS_HEADERS)

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 200)
    data = get_data()
    result = {}
    for region in regions:
        rows = [x for x in data if x["region"] == region]
        if not rows:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue
        lat = [x["latency_ms"] for x in rows]
        up = [x["uptime"] for x in rows]
        sorted_lat = sorted(lat)
        n = len(sorted_lat)
        p95 = sorted_lat[min(int(0.95 * n), n-1)]
        result[region] = {
            "avg_latency": round(sum(lat)/len(lat), 2),
            "p95_latency": round(p95, 2),
            "avg_uptime": round(sum(up)/len(up), 3),
            "breaches": sum(1 for x in lat if x > threshold_ms)
        }
    return JSONResponse(content=result, headers=CORS_HEADERS)
