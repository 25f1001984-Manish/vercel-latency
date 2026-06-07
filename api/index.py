from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os

app = FastAPI()

CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "*"}

@app.options("/")
async def options():
    return JSONResponse({}, headers=CORS)

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 200)
    base = os.path.dirname(__file__)
    with open(os.path.join(base, "..", "q-vercel-latency.json")) as f:
        data = json.load(f)
    result = {}
    for region in regions:
        rows = [x for x in data if x["region"] == region]
        if not rows:
            result[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        lat = sorted([x["latency_ms"] for x in rows])
        up = [x["uptime"] for x in rows]
        result[region] = {
            "avg_latency": round(sum(lat)/len(lat), 2),
            "p95_latency": round(lat[min(int(0.95*len(lat)), len(lat)-1)], 2),
            "avg_uptime": round(sum(up)/len(up), 3),
            "breaches": sum(1 for x in lat if x > threshold_ms)
        }
    return JSONResponse(result, headers=CORS)
