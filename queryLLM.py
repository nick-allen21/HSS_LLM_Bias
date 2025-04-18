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

LLM_Used = "Chat GPT 4"
# Racial/Ethnic Groups 
Groups = [
    "white male", "white female", "black male", "black female", 
    "asian male", "asian female", "hispanic male", "hispanic female"
]

number_responses = 1  # Set to 1 for testing; adjust as needed
# Your API key

# Load variables from .env file
load_dotenv()

# Set API key to the environment variable
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

# Temperature controls how "creative" the model is
TEMPERATURE = 0.7

# Directory with CSV files
csv_directory = "/Users/nickallen/Documents/GitHub/HSS_LLM_Bias"


# The name of the JSON file we will save
output_json_filename = "chatGPT_responses.json"

# -----------------------
# 2. Helper Functions
# -----------------------

def queryLLM(prompt, model="gpt-4", temperature=0.7, max_tokens=100, retries=3, timeout=120):
    """
    Uses the ChatCompletion endpoint to get a response from GPT-4.
    It will try the request up to 'retries' times if a timeout or error occurs.
    """
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout  # Increase timeout to allow more time for a response
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)  # wait 2 seconds before retrying
            else:
                return f"Error: {e}"

def replace_brackets_with_group(text, group):
    """
    Replaces all occurrences of [ ... ] in 'text' (including empty brackets)
    with the string 'group'.
    """
    return re.sub(r"\[.*?\]", group, text)

# -----------------------
# 3. Build Data Structure
# -----------------------

# Gather only CSV files
csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]

# Nested dictionary for storing everything
dataframes_dict = {
    "Eval_Manage": {},
    "Diagnosis": {}
}

for file_name in csv_files:
    file_path = os.path.join(csv_directory, file_name)
    df = pd.read_csv(file_path)
    
    # Clean up file name (remove prefix and extension)
    key_name = file_name.replace("Nick LLM Prompts - ", "").replace(".csv", "")
    
    # Determine whether this file is "Eval_Manage" or "Diagnosis"
    if "eval" in key_name.lower():
        key_name = key_name.replace("_Eval_Manage", "").replace("Eval_Manage", "")
        # Create sub-structure for Eval_Manage files
        dataframes_dict["Eval_Manage"][key_name] = {
            "Original_Df": df,
            "Manufactured_Prompts": {}
        }
        
        # Loop over each group and manufacture new prompts
        for group in Groups:
            dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group] = {}
            # Process only the first 'number_responses' prompts
            for i, original_prompt in enumerate(df["Prompt"]):
                new_prompt = replace_brackets_with_group(original_prompt, group)
                
                correct_anser = df["Correct answer"][i]
                incorrect_answer1 = df["Incorrect Answer 1"][i]
                incorrect_answer2 = df["Incorrect Answer 2"][i] 
                incorrect_answer3 = df["Incorrect Answer 3"][i]
                
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Chat_Responses'] = []
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Correct_Answer'] = correct_anser
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_1'] = incorrect_answer1
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_2'] = incorrect_answer2   
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_3'] = incorrect_answer3
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['idx'] = i
                
                
                print(f"Getting LLM responses for : Eval and Manage, {key_name}, {group}, number {i}. \nPrompt : \n{new_prompt} \n")
                for _ in range(number_responses) : 
                    response = queryLLM(
                        new_prompt,
                        model="gpt-4",
                        temperature=TEMPERATURE,
                        max_tokens=100
                    )
                    dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Chat_Responses'].append(response)
                    gc.collect()
    
    elif "diagnosis" in key_name.lower():
        key_name = key_name.replace("_Diagnosis", "").replace("Diagnosis", "")
        # Create sub-structure for Diagnosis files
        dataframes_dict["Diagnosis"][key_name] = {
            "Original_Df": df,
            "Manufactured_Prompts": {}
        }
        
        # Loop over each group and manufacture new prompts
        for group in Groups:
            dataframes_dict["Diagnosis"][key_name]["Manufactured_Prompts"][group] = {}
            # Process only the first 'number_responses' prompts
            for i, original_prompt in enumerate(df["Prompt"]):
                new_prompt = replace_brackets_with_group(original_prompt, group)
                
                correct_anser = df["Correct answer"][i]
                incorrect_answer1 = df["Incorrect Answer 1"][i]
                incorrect_answer2 = df["Incorrect Answer 2"][i] 
                incorrect_answer3 = df["Incorrect Answer 3"][i]
                
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Chat_Responses'] = []
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Correct_Answer'] = correct_anser
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_1'] = incorrect_answer1
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_2'] = incorrect_answer2   
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['Incorrect_Answer_3'] = incorrect_answer3
                dataframes_dict["Eval_Manage"][key_name]["Manufactured_Prompts"][group][new_prompt]['idx'] = i
                
                
                dataframes_dict["Diagnosis"][key_name]["Manufactured_Prompts"][group][new_prompt] = []
                print(f"Getting LLM responses for : Diagnosis, {key_name}, {group}. \nPrompt : \n{new_prompt} \n")
                for _ in range(number_responses) : 
                    response = queryLLM(
                        new_prompt,
                        model="gpt-4",
                        temperature=TEMPERATURE,
                        max_tokens=100
                    )
                    dataframes_dict["Diagnosis"][key_name]["Manufactured_Prompts"][group][new_prompt]['Chat_Responses'].append(response)
                    gc.collect()

# ---------------------------------------------
# 4. Save as JSON (convert to JSON-friendly format)
# ---------------------------------------------

output_data = {
    "LLM": LLM_Used,
    "Eval_Manage": {},
    "Diagnosis": {}
}

# For Eval_Manage: convert original DF and manufactured prompts
for key, eval_data in dataframes_dict["Eval_Manage"].items():
    output_data["Eval_Manage"][key] = {
        "Original_Df": eval_data["Original_Df"].to_dict(orient='records'),
        "Manufactured_Prompts": eval_data["Manufactured_Prompts"]
    }

# For Diagnosis: convert original DF and manufactured prompts
for diag_key, diag_data in dataframes_dict["Diagnosis"].items():
    output_data["Diagnosis"][diag_key] = {
        "Original_Df": diag_data["Original_Df"].to_dict(orient='records'),
        "Manufactured_Prompts": diag_data["Manufactured_Prompts"]
    }

# Define output folder
results_dir = os.path.join(csv_directory, "results")
os.makedirs(results_dir, exist_ok=True)  # Create "results" folder if it doesn't exist

# Set initial output path
output_path = os.path.join(results_dir, output_json_filename)

# Check if file already exists; if so, append a timestamp
if os.path.exists(output_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(output_json_filename)
    output_json_filename = f"{name}_{timestamp}{ext}"
    output_path = os.path.join(results_dir, output_json_filename)

# Write JSON to file
with open(output_path, "w") as f:
    json.dump(output_data, f, indent=2)

print(f"Done! JSON saved to: {output_path}")
