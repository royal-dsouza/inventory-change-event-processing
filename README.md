# Inventory Change Event Processing Pipeline

A comprehensive, event-driven pipeline for inventory management using Google Cloud services. This project demonstrates ingesting inventory change events (JSON and Protobuf), publishing them to Google Cloud Pub/Sub, processing them with Cloud Run, and scheduling batch summary reports via Cloud Scheduler.

## Problem Statement

Develop a system to capture inventory change events, publish them to Pub/Sub, enforce schemas, trigger low-stock alerts, and schedule nightly summary reports.

## Requirements

1. Create a Pub/Sub topic `inventory-topic` and subscription `inventory-sub`.
2. Implement a Python JSON publisher to read `inventory_adjustments.csv`, serialize to JSON, and publish to `inventory-topic`.
3. Implement a Python JSON subscriber to consume from `inventory-sub` and update a local in-memory store or logs.
4. Define a Protobuf schema in `proto/inventory.proto`, register it in Pub/Sub Schema Registry, and attach to `inventory-topic` with JSON encoding.
5. Implement a Protobuf publisher that uses the registered schema to serialize and publish events.
6. Implement a Protobuf subscriber to deserialize and validate schema-enforced messages.
7. Deploy a Cloud Run service triggered by Pub/Sub to send low-stock alerts for items below threshold.
8. Schedule a nightly Cloud Scheduler job to invoke the Cloud Run summary endpoint via HTTP and generate a report.
9. Configure IAM roles for Pub/Sub, Cloud Run, and Cloud Scheduler.

## Solution

![architecture diagram](architecture.png)

```bash
.
├── csv_data_generator.py       # Reads CSV and yields inventory adjustments
├── json_publisher.py           # Publishes JSON messages to Pub/Sub
├── json_consumer.py            # Subscribes to JSON messages and updates state
├── proto/
│   ├── inventory.proto         # Protobuf schema definition
│   └── inventory_pb2.py        # Generated Protobuf classes
├── protobuf_publisher.py       # Publishes Protobuf-encoded messages
├── protobuf_consumer.py        # Subscribes and validates Protobuf messages
├── low_stock_alert_function.py # Cloud Run Flask app for low-stock alerts
├── main.py                     # HTTP endpoint for nightly summary
├── inventory_adjustments.csv   # Sample input data
├── inventory_state.json        # Local state snapshot
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### 1. Pub/Sub Topic & Subscription

```bash
# Create topic and subscription

gcloud pubsub topics create inventory-topic

gcloud pubsub subscriptions create inventory-sub --topic=inventory-topic
```

### 2. JSON Publisher

```bash
# Read CSV and publish JSON

python csv_data_generator.py | python json_publisher.py
```

### 3. JSON Subscriber

```bash
# Consume JSON events and update local state

python json_consumer.py
```

### 4. Protobuf Schema Registration

```bash
# Register schema and bind to topic

gcloud pubsub schemas create inventory-schema --type=protocol-buffer --definition-file=proto/inventory.proto

gcloud pubsub topics update inventory-topic --schema=inventory-schema --message-encoding=json
```

### 5. Protobuf Publisher

```bash
# Publish Protobuf-encoded events

python csv_data_generator.py | python protobuf_publisher.py
```

### 6. Protobuf Subscriber

```bash
# Consume and validate Protobuf messages

python protobuf_consumer.py
```

### 7. Pub/Sub topic & subscription for low-stock alert
```bash
# create topic & subscription to publish & consume low stock alert message
gcloud pubsub topics create 
low-stock-alerts

gcloud pubsub subscriptions create low-stock-consumer \
  --topic=low-stock-alerts
```

### 8. Storage bucket
```bash
# create storage bucket and upload the inventory state
gsutil mb -l us-central1 gs://inventory-bucket-rd/

gsutil cp inventory_state.json gs://inventory-bucket-rd/
```

### 9. Deploy Low-Stock Alert function


create cloud run function to check for low stock and update the inventory

<img width="823" alt="image" src="https://github.com/user-attachments/assets/92157e0d-b1ea-4d1c-a4c3-6e01ed85cfd8" />
<img width="660" alt="image" src="https://github.com/user-attachments/assets/055cda65-5d5e-4562-80dd-e58d4c706527" />

```bash
# update the source
main.py - low_stock_alert_function.py
requirements.txt -
google-cloud-storage==2.10.0
google-cloud-pubsub==2.17.0
functions-framework==3.3.0
```

### 10. Create a repo in artifact registry
```bash
gcloud artifacts repositories create inventory-change-event-processor-repo \
    --repository-format=docker \
    --location="us-central1"
```

### 11. Setup CI/CD with Cloud Build

dockerfile: Defines build steps for Cloud Run.

cloudbuild.yaml: Builds, pushes, and deploys the service.

Cloud Build trigger is configured to deploy on repository changes.

### 12. Cloud Scheduler Job

```bash
# Create nightly summary job invoking Cloud Run endpoint

gcloud scheduler jobs create http nightly-inventory-summary \
  --location=us-central1 \
  --schedule="0 3 * * *" \
  --uri="https://inventory-report-752749770357.us-central1.run.app" \
  --http-method=GET
```

## Acknowledgements

Developed as part of the GCP Data Engineering Bootcamp assignment, showcasing real-time event-driven architecture on Google Cloud.
