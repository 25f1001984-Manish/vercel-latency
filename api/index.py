from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# Add CORS middleware - this is the primary CORS handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    data = json.load(f)

class Input(BaseModel):
    regions: list[str]
    threshold_ms: float

# Explicit OPTIONS handler for preflight - critical for Vercel
@app.options("/{rest_of_path:path}")
async def preflight(rest_of_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

@app.post("/")
async def metrics(inp: Input):
    result = {}

    for region in inp.regions:
        rows = [x for x in data if x["region"] == region]
        lat = [x["latency_ms"] for x in rows]
        up = [x["uptime_pct"] for x in rows]

        result[region] = {
            "avg_latency": round(sum(lat) / len(lat), 2),
            "p95_latency": round(float(np.percentile(lat, 95)), 2),
            "avg_uptime": round(sum(up) / len(up), 3),
            "breaches": sum(1 for x in lat if x > inp.threshold_ms),
        }

    return JSONResponse(
        content=result,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )
