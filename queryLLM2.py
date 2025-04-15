import os
import re
import gc
import json
import time
import datetime
import pandas as pd
import openai
from dotenv import load_dotenv

# -----------------------
# 1. Setup & Configuration
# -----------------------

LLM_USED = "Chat GPT 4"

# Groups to use in prompts
GROUPS = [
    "white male", "white female", "black male", "black female", 
    "asian male", "asian female", "hispanic male", "hispanic female"
]

NUMBER_RESPONSES = 1
TEMPERATURE = 0.7
MAX_TOKENS = 100
TIMEOUT = 120

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directory with CSVs and output
csv_directory = "/Users/nickallen/Documents/GitHub/HSS_LLM_Bias/Nick_LLM_Prompts"
OUTPUT_FILENAME = "chatGPT_responses.json"
RESULTS_DIR = os.path.join(csv_directory, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# -----------------------
# 2. Helper Functions
# -----------------------

def query_llm(prompt, model="gpt-4", temperature=TEMPERATURE, max_tokens=MAX_TOKENS, retries=3, timeout=TIMEOUT):
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return f"Error: {e}"

def replace_brackets_with_group(text, group):
    return re.sub(r"\[.*?\]", group, text)


# -----------------------
# 3. Main Loop
# -----------------------

results = []
csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
print(f"Found {len(csv_files)} CSV files in {csv_directory}.")

for file_name in csv_files:
    domain = "Eval_Manage" if "eval" in file_name.lower() else "Diagnosis" if "diagnosis" in file_name.lower() else None
    if not domain:
        print(f"Skipping file: {file_name} | Domain not recognized.")
        continue
    
    print(f"\nProcessing file: {file_name} | Domain: {domain}")
    
    # Clean file label for output
    domain_key = file_name.replace("Nick LLM Prompts - ", "").replace(".csv", "")
    domain_key = domain_key.replace("Eval_Manage", "").replace("Diagnosis", "").replace("_", "").strip()

    file_path = os.path.join(csv_directory, file_name)
    df = pd.read_csv(file_path)

    for group in GROUPS:
        for i, row in df.iterrows():
            new_prompt = replace_brackets_with_group(row["Prompt"], group)
            print(f"→ {domain} | {domain_key} | {group} | Prompt #{i}\n{new_prompt}\n")

            chat_responses = []
            for j in range(NUMBER_RESPONSES):
                print(f"Attempting to get response {j+1})")
                response = query_llm(new_prompt)
                chat_responses.append(response)
                gc.collect()

            results.append({
            "prompt_info": {
                "domain": domain,
                "file": domain_key,
                "group": group,
                "idx": i,
                "subspecialty": row.get("Subspecialty", ""),
                "source": row.get("Source", ""),
                "differential_formation": row.get("Differential Formation", ""),
                "treatment_strategies": row.get("Treatment Stragies", ""),
                "prompt": new_prompt
            },
            "answer_key": {
                "correct": row.get("Correct answer", ""),
                "incorrect_1": row.get("Incorrect Answer 1", ""),
                "incorrect_2": row.get("Incorrect Answer 2", ""),
                "incorrect_3": row.get("Incorrect Answer 3", "")
            },
            "chat_responses": chat_responses
            })

# -----------------------
# 4. Save Output
# -----------------------

# Check if filename already exists
output_path = os.path.join(RESULTS_DIR, OUTPUT_FILENAME)
if os.path.exists(output_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(OUTPUT_FILENAME)
    output_path = os.path.join(RESULTS_DIR, f"{base}_{timestamp}{ext}")

# Write flat JSON list
with open(output_path, "w") as f:
    json.dump({
        "LLM": LLM_USED,
        "results": results
    }, f, indent=2)
