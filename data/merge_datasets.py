import csv
import os

# Define mappings based on analysis
# text.csv: 0:sadness, 1:joy, 2:love, 3:anger, 4:fear, 5:surprise
LABEL_MAPPING = {
    '0': 'sadness',
    '1': 'joy',
    '2': 'love',
    '3': 'anger',
    '4': 'fear',
    '5': 'surprise'
}

TRAIN_TXT_PATH = r'd:\project ai\data\train.txt'
TEXT_CSV_PATH = r'd:\project ai\data\text.csv'
OUTPUT_PATH = r'd:\project ai\data\emotions_combined.csv'

def process_text_csv(filepath):
    data = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'text' in row and 'label' in row:
                original_label = row['label']
                if original_label in LABEL_MAPPING:
                    normalized_label = LABEL_MAPPING[original_label]
                    data.append({'text': row['text'], 'label': normalized_label})
    return data

def process_train_txt(filepath):
    data = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ';' in line:
                text, label = line.rsplit(';', 1)
                data.append({'text': text, 'label': label})
    return data

def main():
    print("Reading text.csv...")
    csv_data = process_text_csv(TEXT_CSV_PATH)
    print(f"Found {len(csv_data)} records in text.csv")

    print("Reading train.txt...")
    txt_data = process_train_txt(TRAIN_TXT_PATH)
    print(f"Found {len(txt_data)} records in train.txt")

    combined_data = csv_data + txt_data
    print(f"Total records: {len(combined_data)}")

    print(f"Writing to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'label'])
        writer.writeheader()
        writer.writerows(combined_data)
    
    print("Done.")

if __name__ == "__main__":
    main()
