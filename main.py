from google.cloud import storage
import json
import os
from flask import jsonify, request, Flask

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
#     "GOOGLE_APPLICATION_CREDENTIALS",
#     "/Users/royaldsouza/Downloads/my_gcp_project.json"
# )

app = Flask(__name__)


bucket_name =  "inventory-bucket-rd"
low_stock_threshold = 20


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

@app.route("/", methods=["GET"])
def main():
    """Generate an inventory report."""
    if request.method != "GET":
        return "Method not allowed", 405

    try:
        # Load the current inventory state
        inventory_state = load_inventory_state()

        # Generate summary report
        report = {
            "total_items": len(inventory_state),
            "low_stock_items": [item for item, qty in inventory_state.items() if qty < low_stock_threshold],
            "inventory_state": inventory_state
        }
        print(f"Generated inventory report: {report}")

        return jsonify(report), 200
    except Exception as e:
        print(f"Error generating inventory report: {e}")
        return "Error generating inventory report", 500
    
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=PORT)