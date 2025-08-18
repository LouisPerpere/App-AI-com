# helpers_debug.py
from bson import ObjectId

def build_owner_filter(user_id: str):
    """Build owner filter tolerant to different field names and types"""
    # filtre tolérant aux types et aux schémas hétérogènes
    parts = [{"owner_id": user_id}, {"ownerId": user_id}]
    try:
        oid = ObjectId(user_id)
        parts += [{"owner_id": oid}, {"ownerId": oid}]
    except Exception:
        pass
    return {"$or": parts}