from google.cloud import pubsub_v1
import os
import json
import csv
from inventory_pb2 import InventoryEvent

# ─── Configuration ────────────────────────────────────────────────────────────
# Point to your service account key for local development.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/royaldsouza/Downloads/my_gcp_project.json"
)
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "elevated-column-458305-f8")
topic_id   = os.getenv("PUBSUB_TOPIC", "inventory-topic")
csv_path   = os.getenv("CSV_FILE_PATH", "inventory_adjustments.csv")
# ─── End Configuration ────────────────────────────────────────────────────────

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def protobuf_to_json(event):
    """
    Convert a Protobuf message to JSON bytes that match the schema encoding.
    """
    payload = {
        "item_id":   event.item_id,
        "adjustment": event.adjustment,
        "timestamp": event.timestamp
    }
    return json.dumps(payload).encode("utf-8")

with open(csv_path, mode="r", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Build the Protobuf message
        event = InventoryEvent(
            item_id   = row["item_id"],
            adjustment = int(row["adjustment"]),
            timestamp = row["timestamp"]
        )

        # Serialize as JSON for Pub/Sub
        data = protobuf_to_json(event)

        # Publish and optionally add attributes if you need them
        future = publisher.publish(topic_path, data=data)
        message_id = future.result()
        print(f"Published JSON-encoded message ID {message_id} for {event.item_id}")
