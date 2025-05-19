from google.cloud import pubsub_v1
import os
import json

# Project configuration
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/Users/royaldsouza/Downloads/my_gcp_project.json") # for local dev
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE # for local dev
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "elevated-column-458305-f8")

subscription_id = os.getenv("SUBSCRIPTION_ID", "inventory-sub")
subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, subscription_id)

inventory_store = {"ITEM00001": 100, "ITEM00002": 50, "ITEM00003": 75, "ITEM00004": 120, "ITEM00005": 90, "ITEM00006": 60, "ITEM00007": 80, "ITEM00008": 110, "ITEM00009": 70, "ITEM00010": 130}  # e.g., {item_id: quantity}

def validate_event(event):
    """
    Validate the event structure and data types.
    """
    required_fields = ["item_id", "adjustment", "timestamp"]
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing field: {field}")
    
    if not isinstance(event["item_id"], str) or not event["item_id"]:
        raise ValueError("item_id must be a non-empty string")
    
    if not isinstance(event["adjustment"], (int)) or not event["adjustment"]:
        raise ValueError("adjustment must be a non-empty integer")
    
    if not isinstance(event["timestamp"], str) or not event["timestamp"]:
        raise ValueError("timestamp must be a non-empty string")

def callback(message):
    try:
        event = json.loads(message.data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        message.nack()
        return
    
    try:
        validate_event(event)
        print(f"Event validated")
    except ValueError as e:
        print(f"[ERROR] Event validation failed: {e}")
        message.nack()
        return
    # Process the event
    # Update the inventory store
    item = event["item_id"]
    change = int(event["adjustment"])
    inventory_store[item] = inventory_store.get(item, 0) + change
    print(f"Updated {item}: {inventory_store[item]}")
    message.ack()

streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
print(f"Listening for messages on {subscription_id}...")

# Keep the main thread alive
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
    print("Subscriber stopped.")