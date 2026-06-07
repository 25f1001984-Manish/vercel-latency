from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

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


@app.post("/")
async def calculate(inp: Input):

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
