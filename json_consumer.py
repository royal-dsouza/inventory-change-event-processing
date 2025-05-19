import json
import os
from google.cloud import pubsub_v1

# Project configuration
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/Users/royaldsouza/Downloads/my_gcp_project.json") # for local dev
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE # for local dev
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "elevated-column-458305-f8")

subscription_id = os.getenv("SUBSCRIPTION_ID", "inventory-sub")
subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, subscription_id)

inventory_store = {"ITEM00001": 100, "ITEM00002": 50, "ITEM00003": 75, "ITEM00004": 120, "ITEM00005": 90, "ITEM00006": 60, "ITEM00007": 80, "ITEM00008": 110, "ITEM00009": 70, "ITEM00010": 130}  # e.g., {item_id: quantity}

def callback(message):
    event = json.loads(message.data.decode("utf-8"))
    item = event["item_id"]
    change = int(event["adjustment"])
    inventory_store[item] = inventory_store.get(item, 0) + change
    print(f"Updated {item}: {inventory_store[item]}")
    message.ack()

streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
print(f"Listening for messages on {sub_path}...")

# Keep the main thread alive
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
    print("Subscriber stopped.")