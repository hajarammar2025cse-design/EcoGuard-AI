"""
Environmental Alerts Service Layer
Manages alerts collection in MongoDB, handles real-time risk notifications,
and supports state transitions (ACTIVE -> ACKNOWLEDGED -> RESOLVED).
"""
from datetime import datetime, timedelta
from bson import ObjectId
from config.db import get_alerts_col, serialize_docs, serialize_doc

def create_alert(alert_type, location, severity, message, status="ACTIVE"):
    """
    Inserts a new environmental alert into MongoDB.
    Performs rate-limiting / deduplication within a 15-minute window for identical alerts.
    """
    col = get_alerts_col()
    recent_cutoff = datetime.utcnow() - timedelta(minutes=15)

    existing = col.find_one({
        "alert_type": alert_type,
        "location": location,
        "status": "ACTIVE",
        "timestamp": {"$gte": recent_cutoff}
    })

    if existing:
        # Update existing alert timestamp rather than creating duplicate
        col.update_one(
            {"_id": existing["_id"]},
            {"$set": {"timestamp": datetime.utcnow(), "severity": severity, "message": message}}
        )
        return serialize_doc(existing)

    alert_doc = {
        "alert_type": alert_type,
        "location": location,
        "severity": severity,  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        "message": message,
        "timestamp": datetime.utcnow(),
        "status": status       # 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'
    }

    res = col.insert_one(alert_doc)
    alert_doc["_id"] = res.inserted_id
    return serialize_doc(alert_doc)

def get_alerts(status=None, severity=None, alert_type=None, location=None, limit=100):
    col = get_alerts_col()
    query = {}
    if status and status != 'ALL':
        query["status"] = status
    if severity and severity != 'ALL':
        query["severity"] = severity
    if alert_type and alert_type != 'ALL':
        query["alert_type"] = alert_type
    if location and location != 'ALL':
        query["location"] = location

    cursor = col.find(query).sort("timestamp", -1).limit(limit)
    return serialize_docs(cursor)

def update_alert_status(alert_id, new_status):
    col = get_alerts_col()
    try:
        col.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
        return True
    except Exception as e:
        print(f"Error updating alert status: {e}")
        return False
