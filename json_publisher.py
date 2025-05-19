import csv
import json
import os
from google.cloud import pubsub_v1

# Project configuration
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/Users/royaldsouza/Downloads/my_gcp_project.json") # for local dev
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE # for local dev

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "elevated-column-458305-f8")
topic_id = os.getenv("PUBSUB_TOPIC", "inventory-topic")

csv_file_path = os.getenv("CSV_FILE_PATH", "inventory_adjustments.csv")

with open(csv_file_path, mode="r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Convert the row to a JSON string then encode it to bytes
        data = json.dumps(row).encode("utf-8")
        
        # Create a Pub/Sub client and topic path
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        
        # Publish the message to the topic
        future = publisher.publish(topic_path, data)
        
        # Wait for the publish to complete
        future.result()

        print(f"Published message ID: {future.result()} for item_id: {row['item_id']}")