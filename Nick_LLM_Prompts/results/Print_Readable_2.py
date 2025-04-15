import re
import json
from fpdf import FPDF

def safe_str(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)

def force_word_break(text, max_chars=10):
    """
    Insert a space or hyphen after every 'max_chars' of non-whitespace characters,
    so extremely long text can wrap.
    """
    pattern = rf"(\S{{{max_chars}}})"
    # Insert a zero-width space or a hyphen (your choice). For demonstration, we use a space:
    return re.sub(pattern, r"\1 ", text)

file_path = "/Users/nickallen/Documents/GitHub/HSS_LLM_Bias/Nick_LLM_Prompts/results/chatGPT_responses_20250414_191252.json"

cur_file = None

with open(file_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)
    data = json_data["results"]

formatted_lines = []
for idx in range(15):
    formatted_lines.append(f"=== Results for idx {idx} ===")
    entries_for_idx = [entry for entry in data if entry.get("idx") == idx]

    if not entries_for_idx:
        formatted_lines.append("No entries found for this idx.")
        formatted_lines.append("")
        continue

    for i, entry in enumerate(entries_for_idx):
        next_file = entry.get("file", "N/A")
        first = False
        if cur_file is None:
            first = True
            cur_file = entry.get("file", "N/A")
            next_file = entry.get("file", "N/A")
            
        if cur_file != next_file or first:
            formatted_lines.append(f"=== Results for {next_file} ===")
            formatted_lines.append(f"File: {next_file}")
            cur_file = next_file
            
            formatted_lines.append("Correct Answer:")
            formatted_lines.append(safe_str(entry.get("correct", "N/A")))

            formatted_lines.append("Incorrect Options:")
            formatted_lines.append("  1. " + safe_str(entry.get("incorrect_1", "N/A")))
            formatted_lines.append("  2. " + safe_str(entry.get("incorrect_2", "N/A")))
            formatted_lines.append("  3. " + safe_str(entry.get("incorrect_3", "N/A \n")))
            
        if i == 0 and not first:
            formatted_lines.append("Correct Answer:")
            formatted_lines.append(safe_str(entry.get("correct", "N/A")))

            formatted_lines.append("Incorrect Options:")
            formatted_lines.append("  1. " + safe_str(entry.get("incorrect_1", "N/A")))
            formatted_lines.append("  2. " + safe_str(entry.get("incorrect_2", "N/A")))
            formatted_lines.append("  3. " + safe_str(entry.get("incorrect_3", "N/A")))
        else:
            formatted_lines.append("Group:")
            formatted_lines.append(safe_str(entry.get("group", "N/A")))

            formatted_lines.append("Prompt:")
            formatted_lines.append(safe_str(entry.get("prompt", "N/A")))

            formatted_lines.append("Chat Responses:")
            formatted_lines.append(safe_str(entry.get("chat_responses", "N/A")))
        
        formatted_lines.append("")  # spacing
    formatted_lines.append("")

formatted_text = "\n".join(formatted_lines)

# Print to console
print(formatted_text)

# Save to text
with open("output.txt", "w", encoding="utf-8") as text_file:
    text_file.write(formatted_text)

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=10)  # Enables auto page break
pdf.set_margins(10, 10, 10)                   # Sets left, top, right margins
pdf.add_page()
pdf.set_font("Helvetica", size=12)

for raw_line in formatted_text.split("\n"):
    # Force breaks in lines that might be too long
    line = force_word_break(raw_line, max_chars=60)
    pdf.multi_cell(0, 10, line)

pdf.output("output.pdf")
print("Saved 'output.txt' and 'output.pdf'.")
