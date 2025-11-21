import os
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Bots Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db  # type: ignore

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # noqa: BLE001
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:  # noqa: BLE001
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------------
# Mock Data Generators
# -----------------------------
TOKENS = ["SOL", "BONK", "JUP", "PYTH", "WIF", "GECKO", "ORCA", "MNGO", "RAY", "USDC"]
STRATEGIES = [
    {"name": "MeanRevert", "version": "1.4.2"},
    {"name": "Momentum", "version": "2.1.0"},
    {"name": "ArbX", "version": "0.9.7"},
    {"name": "LLMScout", "version": "0.6.5"},
    {"name": "GridAlpha", "version": "3.0.1"},
]
PLAYERS = [f"Player-{i:02d}" for i in range(1, 13)]
STATUSES = ["Searching", "In Position", "Managing", "Exiting"]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def pct(a: float, b: float) -> float:
    return 0.0 if b == 0 else round((a / b) * 100, 2)


@app.get("/api/dashboard/summary")
def dashboard_summary(timeframe: str = "24h") -> Dict[str, Any]:
    total_revenue_sol = round(random.uniform(120.0, 620.0), 2)
    active_positions = random.randint(8, 42)
    closed_positions = random.randint(50, 320)
    wins = random.randint(25, closed_positions) if closed_positions else 0
    win_rate = pct(wins, closed_positions)

    secondary = {
        "last_hour_pnl": round(random.uniform(-3.5, 6.0), 2),
        "at_risk": random.randint(0, 6),
        "players_in": {
            "count": random.randint(4, len(PLAYERS)),
            "pct": round(random.uniform(25, 95), 1),
        },
        "concentration": random.choice(["bullish", "bearish", "neutral"]),
        "best_asset": {"token": random.choice(TOKENS), "pct": round(random.uniform(3, 28), 2)},
        "worst_asset": {"token": random.choice(TOKENS), "pct": round(random.uniform(-22, -1), 2)},
    }

    return {
        "timeframe": timeframe,
        "kpis": {
            "total_revenue_sol": total_revenue_sol,
            "total_revenue_change_pct": round(random.uniform(-8, 18), 2),
            "active_positions": active_positions,
            "active_positions_change_pct": round(random.uniform(-12, 15), 2),
            "closed_positions": closed_positions,
            "closed_positions_change_pct": round(random.uniform(-10, 10), 2),
            "win_rate_pct": win_rate,
            "avg_performance_pct": round(random.uniform(-1.2, 3.2), 2),
        },
        "secondary": secondary,
    }


@app.get("/api/dashboard/live-pnl")
def live_pnl(points: int = 60) -> Dict[str, Any]:
    points = max(20, min(points, 240))
    start = now_utc() - timedelta(minutes=points)
    data = []
    for i in range(points):
        ts = start + timedelta(minutes=i)
        val = round(random.uniform(-5, 5), 2)
        # add some outliers
        if random.random() < 0.05:
            val = round(random.uniform(-18, 18), 2)
        data.append({"t": ts.isoformat(), "v": val})
    return {"series": data}


@app.get("/api/positions/open")
def open_positions() -> Dict[str, Any]:
    rows = []
    for _ in range(random.randint(12, 28)):
        player = random.choice(PLAYERS)
        status = random.choice(STATUSES)
        token = random.choice(TOKENS)
        strat = random.choice(STRATEGIES)
        enter_time = now_utc() - timedelta(minutes=random.randint(10, 360))
        pnl_sol = round(random.uniform(-3.2, 6.5), 3)
        pnl_pct = round(random.uniform(-12, 22), 2)
        rows.append({
            "player": player,
            "connected": random.random() > 0.08,
            "status": status,
            "token": token,
            "strategy": f"{strat['name']} {strat['version']}",
            "time_in_position": random.randint(5, 360),
            "pnl_sol": pnl_sol,
            "pnl_pct": pnl_pct,
            "entered_at": enter_time.isoformat(),
        })
    header = {
        "searching": sum(1 for r in rows if r["status"] == "Searching"),
        "in_position": sum(1 for r in rows if r["status"] == "In Position"),
        "managing": sum(1 for r in rows if r["status"] == "Managing"),
        "exiting": sum(1 for r in rows if r["status"] == "Exiting"),
    }
    return {"summary": header, "rows": rows}


@app.get("/api/positions/closed")
def closed_positions() -> Dict[str, Any]:
    rows = []
    for _ in range(random.randint(30, 80)):
        player = random.choice(PLAYERS)
        token = random.choice(TOKENS)
        strat = random.choice(STRATEGIES)
        duration = random.randint(3, 720)
        close_time = now_utc() - timedelta(hours=random.randint(1, 72))
        pnl_sol = round(random.uniform(-7.5, 12.0), 3)
        pnl_pct = round(random.uniform(-25, 42), 2)
        rows.append({
            "team": random.choice(["Alpha", "Beta", "Gamma", "Delta"]),
            "player": player,
            "token": token,
            "strategy": f"{strat['name']} {strat['version']}",
            "pnl_sol": pnl_sol,
            "pnl_pct": pnl_pct,
            "duration_min": duration,
            "closed_at": close_time.isoformat(),
        })
    return {"rows": rows}


@app.get("/api/concentration/tokens")
def token_concentration() -> Dict[str, Any]:
    items = []
    for t in TOKENS:
        items.append(
            {
                "token": t,
                "pools": random.randint(1, 14),
                "risk": random.choice(["Low", "Medium", "High"]),
                "pnl_sol": round(random.uniform(-25, 60), 2),
            }
        )
    return {"items": items}


@app.get("/api/deployment/strategies")
def strategy_deployment() -> Dict[str, Any]:
    items = []
    for s in STRATEGIES:
        items.append(
            {
                "strategy": s["name"],
                "version": s["version"],
                "players": random.randint(1, len(PLAYERS)),
                "positions_opened": random.randint(10, 850),
                "pnl_sol": round(random.uniform(-45, 220), 2),
            }
        )
    return {"items": items}


@app.get("/api/strategies/best")
def best_strategies() -> Dict[str, Any]:
    items = []
    for s in STRATEGIES:
        items.append(
            {
                "strategy": f"{s['name']} {s['version']}",
                "positions": random.randint(50, 900),
                "total_pnl_sol": round(random.uniform(10, 520), 2),
                "avg_pct": round(random.uniform(1.5, 12.0), 2),
                "win_rate": round(random.uniform(52, 78), 2),
            }
        )
    items.sort(key=lambda x: x["total_pnl_sol"], reverse=True)
    return {"items": items[:3]}


@app.get("/api/strategies/worst")
def worst_strategies() -> Dict[str, Any]:
    items = []
    for i in range(3):
        s = random.choice(STRATEGIES)
        items.append(
            {
                "strategy": f"{s['name']} {s['version']}",
                "positions": random.randint(40, 600),
                "total_pnl_sol": round(random.uniform(-220, -5), 2),
                "avg_pct": round(random.uniform(-12.0, -0.5), 2),
                "win_rate": round(random.uniform(22, 48), 2),
            }
        )
    items.sort(key=lambda x: x["total_pnl_sol"])  # most negative first
    return {"items": items}


@app.get("/api/performance/tokens")
def token_performance(timeframe: str = "today") -> Dict[str, Any]:
    bars = []
    for t in TOKENS:
        bars.append({"token": t, "pnl_sol": round(random.uniform(-40, 80), 2)})
    return {"timeframe": timeframe, "bars": bars}


@app.get("/api/monitor/overview")
def monitor_overview() -> Dict[str, Any]:
    # hourly bars for last 24h
    bars = []
    start = now_utc() - timedelta(hours=24)
    for i in range(24):
        ts = start + timedelta(hours=i)
        bars.append({"t": ts.isoformat(), "v": round(random.uniform(-15, 22), 2)})
    stats = {
        "net_pnl": round(sum(b["v"] for b in bars), 2),
        "total_positions": random.randint(60, 420),
        "profitable_hours": sum(1 for b in bars if b["v"] > 0),
        "avg_per_hour": round(sum(b["v"] for b in bars) / len(bars), 2),
    }
    return {"bars": bars, "stats": stats}


@app.get("/api/feed")
def live_feed(limit: int = 30) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    base = now_utc()
    for i in range(limit):
        ts = base - timedelta(minutes=i * random.randint(1, 3))
        action = random.choice(["OPEN", "CLOSE", "ALERT", "ADJUST"])
        player = random.choice(PLAYERS)
        token = random.choice(TOKENS)
        pnl = round(random.uniform(-8, 14), 2) if action in ("CLOSE", "ADJUST") else None
        items.append(
            {
                "id": 10_000 + i,
                "player": player,
                "action": action,
                "token": token,
                "timestamp": ts.isoformat(),
                "pnl": pnl,
            }
        )
    return {"items": items}


@app.get("/api/alerts")
def alerts() -> Dict[str, Any]:
    # Emit a few transient alerts sometimes
    possible = [
        "Player has not sent a heartbeat",
        "RPC latency elevated",
        "New strategy version available",
        "Wallet balance low",
        "High slippage detected",
    ]
    items = []
    for _ in range(random.randint(0, 2)):
        items.append(
            {
                "level": random.choice(["info", "warning", "error"]),
                "message": random.choice(possible),
                "timestamp": now_utc().isoformat(),
            }
        )
    return {"items": items}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
