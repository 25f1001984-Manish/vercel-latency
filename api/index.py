from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import numpy as np
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "q-vercel-latency.json"), "r") as f:
    data = json.load(f)


class Input(BaseModel):
    regions: list[str]
    threshold_ms: float


# Handle CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


# POST endpoint
@app.post("/")
async def metrics(inp: Input):

    result = {}

    for region in inp.regions:

        rows = [x for x in data if x["region"] == region]

        latencies = [x["latency_ms"] for x in rows]
        uptimes = [x["uptime_pct"] for x in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": len(
                [x for x in latencies if x > inp.threshold_ms]
            )
        }

    return result
