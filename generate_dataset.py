import json
import os
import zipfile

ZIP_PATH = "hotpot_dev_distractor_v1.json.zip"
OUTPUT_PATH = "data/hotpot_100_real.json"

def main():
    print(f"Reading from {ZIP_PATH}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as z:
            json_filename = [name for name in z.namelist() if name.endswith('.json')][0]
            with z.open(json_filename) as f:
                data = json.loads(f.read().decode('utf-8'))
                
        print(f"Loaded {len(data)} base records from zip. Processing the first 100...")
        output_data = []
        for idx, item in enumerate(data[:100]):
            context = []
            for ctx in item.get('context', []):
                title = ctx[0]
                text = "".join(ctx[1])
                context.append({"title": title, "text": text})
                
            qa_example = {
                "qid": item.get('_id', f"q_{idx}"),
                "difficulty": item.get('level', "medium"),
                "question": item.get('question', ""),
                "gold_answer": item.get('answer', ""),
                "context": context
            }
            output_data.append(qa_example)

        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Successfully generated {len(output_data)} REAL records to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
