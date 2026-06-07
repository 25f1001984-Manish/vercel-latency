from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    data = json.load(f)

class Input(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/")
def metrics(inp: Input):

    result = {}

    for region in inp.regions:

        rows = [x for x in data if x["region"] == region]

        lat = [x["latency_ms"] for x in rows]
        up = [x["uptime_pct"] for x in rows]

        result[region] = {
            "avg_latency": round(sum(lat)/len(lat),2),
            "p95_latency": round(float(np.percentile(lat,95)),2),
            "avg_uptime": round(sum(up)/len(up),3),
            "breaches": sum(1 for x in lat if x > inp.threshold_ms)
        }

    return result
