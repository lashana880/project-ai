import csv
import collections

INPUT_PATH = r'd:\project ai\data\emotions_combined.csv'

def verify_dataset(filepath):
    print(f"Verifying {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers != ['text', 'label']:
                print(f"ERROR: Unexpected headers: {headers}")
                return

            label_counts = collections.Counter()
            row_count = 0
            for row in reader:
                label_counts[row['label']] += 1
                row_count += 1
            
            print(f"Total rows: {row_count}")
            print("Label distribution:")
            for label, count in label_counts.most_common():
                print(f"  {label}: {count}")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_dataset(INPUT_PATH)
