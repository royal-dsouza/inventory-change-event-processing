from cloudevents.http import CloudEvent
import base64
import json
import os
from low_stock_alert_function import pubsub_event
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/royaldsouza/Downloads/my_gcp_project.json"
)

# Sample Pub/Sub message data
message_data = {
    "item_id": "ITEM00001",
    "adjustment": 5
}

bucket_name = "inventory-bucket-rd"

# Encode the message data as base64
encoded_data = base64.b64encode(json.dumps(message_data).encode("utf-8")).decode("utf-8")

print(f"Encoded data: {encoded_data}")
def load_inventory_state():
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
    
load_inventory_state()

# # Create a CloudEvent object
# attributes = {
#     "type": "google.cloud.pubsub.topic.v1.messagePublished",
#     "source": "//pubsub.googleapis.com/projects/YOUR_PROJECT_ID/topics/YOUR_TOPIC_NAME",
# }

# data = {
#     "message": {
#         "data": encoded_data
#     }
# }

# event = CloudEvent(attributes, data)

# # Call the function with the test event
# pubsub_event(event)