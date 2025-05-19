import csv
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "inventory_adjustments.csv"  # Name of the CSV to generate
NUM_RECORDS = 10                        # Total number of rows 
ADJ_MIN, ADJ_MAX = -20, 20                 # Adjustment range (negative for decrements)
START_TIME = datetime.utcnow() - timedelta(days=30)  # Earliest timestamp (30 days ago) 
TIME_SPAN_DAYS = 30                        # Span in days from START_TIME 

def random_timestamp(start, span_days):
    """Generate a random ISO timestamp within the past span_days from start."""
    delta = timedelta(seconds=random.randint(0, span_days * 24 * 3600))
    return (start + delta).isoformat()

def main(num_records):
    with open(OUTPUT_FILE, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)                                       
        writer.writerow(["item_id", "adjustment", "timestamp"])                

        for i in range(1, num_records + 1):
            item_id    = f"ITEM{i:05d}"
            adjustment = random.randint(ADJ_MIN, ADJ_MAX)             
            timestamp  = random_timestamp(START_TIME, TIME_SPAN_DAYS)       
            writer.writerow([item_id, adjustment, timestamp])          

    print(f"Generated {num_records} records in '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main(NUM_RECORDS)
