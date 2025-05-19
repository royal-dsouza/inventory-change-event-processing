"""
Cloud Run Function for Low Stock Alerts - Triggered by Pub/Sub messages
or HTTP requests for inventory alert processing.
"""
import base64
import functions_framework
import os
from google.cloud import storage
import json
from google.cloud import pubsub_v1
from flask import jsonify, request

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/royaldsouza/Downloads/my_gcp_project.json"
)


low_stock_threshold = 20  # Define your low stock threshold

bucket_name = "inventory-bucket-rd"

def load_inventory_state():
    """Load the inventory state from a file in Cloud Storage."""

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob("inventory_state.json")
        data = blob.download_as_text()
        inventory_state = json.loads(data)
        print(f"Loaded inventory state: {inventory_state}")
        return inventory_state
    except Exception as e:
        print(f"Error loading inventory state: {e}")
        return {}

def update_inventory_state(inventory_state, item_id, adjustment):
    """Update the inventory state with the new quantity."""
    inventory_state[item_id] = inventory_state.get(item_id, 0) + adjustment
    print(f"Updated inventory state for item {item_id}: {inventory_state[item_id]}")

    return inventory_state

def check_low_stock(inventory_state):
    """Check for low stock items and return a list of alerts."""
    low_stock_items = []
    for item_id, quantity in inventory_state.items():
        if quantity < low_stock_threshold:
            low_stock_items.append(item_id)
    return low_stock_items
    print(f"Low stock items: {low_stock_items}")

def save_inventory_state(inventory_state):
    """Save the inventory state to a file in Cloud Storage."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob("inventory_state.json")
        blob.upload_from_string(json.dumps(inventory_state))
        print(f"Saved inventory state: {inventory_state}")
    except Exception as e:
        print(f"Error saving inventory state: {e}")

def send_push_notification(alert):
    """Send a push notification for low stock items."""
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.getenv("GOOGLE_CLOUD_PROJECT"), "low-stock-alerts")
        data = json.dumps(alert).encode("utf-8")
        publisher.publish(topic_path, data=data)
        print(f"Push notification sent for low stock items: {alert}")
    except Exception as e:
        print(f"Error sending push notification: {e}") 

@functions_framework.cloud_event
def pubsub_event(cloud_event):
    """Handle Pub/Sub events."""
    try:
        data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        event = json.loads(data)
        item_id = event["item_id"]
        adjustment = int(event["adjustment"])
        print(f"Received event: {event}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Invalid event data: {e}")
        return
    
    # Load the current inventory state
    inventory_state = load_inventory_state()

    # Update the inventory state
    inventory_state = update_inventory_state(inventory_state, item_id, adjustment)

    # Check for low stock items
    low_stock_items = check_low_stock(inventory_state)
    if low_stock_items:
        print(f"Low stock alert for items: {low_stock_items}")
        # Send push notification
        send_push_notification(low_stock_items)

    else:
        print("No low stock items.")
    # Save the updated inventory state back to Cloud Storage
    """Update the inventory state in Cloud Storage."""
    save_inventory_state(inventory_state)
    print(f"Updated inventory state for item {item_id}: {inventory_state[item_id]}")