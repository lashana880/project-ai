
import csv
import collections

def analyze_train_txt(filepath):
    labels = collections.Counter()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if ';' in line:
                _, label = line.strip().rsplit(';', 1)
                labels[label] += 1
    return labels

def analyze_text_csv(filepath):
    labels = collections.Counter()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'label' in row:
                labels[row['label']] += 1
    return labels

print("Train.txt labels:", analyze_train_txt('d:/project ai/data/train.txt'))
print("Text.csv labels:", analyze_text_csv('d:/project ai/data/text.csv'))
