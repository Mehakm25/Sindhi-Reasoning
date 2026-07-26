#!/usr/bin/env python3
import gradio as gr
import openai
import json
import pandas as pd
import os

# ---------- Your generate function ----------
def generate(api_key: str, detailed_prompt: str, model: str = "gpt-4o",
                        max_tokens: int = 2000, temperature: float = 0.7) -> str:
    """
    Generates Sindhi text using OpenAI's chat model based on a provided prompt.
    """
    # Create the client using the provided API key.
    # (If needed, adjust this to match your openai library version.)
    client = openai.Client(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates high-quality reasoning instructions in the Sindhi language based on user input."
            },
            {
                "role": "user",
                "content": detailed_prompt
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response.choices[0].message.content.strip()

# ---------- Global Variables ----------
api_key = #use API key here 
model = "gpt-4o"

# Fixed prompt text (instruction) as provided:
fixed_prompt = '''
You are a helpful assistant that generates reasoning-based instructions in Sindhi. Your task is to generate tasks involving *Causal* and *Commonsense* reasoning based on user-provided factual text.

---

 Reasoning Types:

1.⁠ ⁠*Causal Reasoning*: Identifying a cause and its effect.
2.⁠ ⁠*Commonsense Reasoning*: Use everyday knowledge to infer something.

---

 For each reasoning type, generate:
•⁠  ⁠*Instruction* (in Sindhi): A reasoning-based question or task, not just factual recall.
•⁠  ⁠*Input* (in Sindhi): A relevant scenario or fact.
•⁠  ⁠*Output* (in Sindhi): A well-reasoned response (4–5 lines), showing logical inference.

---

 Example 1 — Inductive Reasoning

*Fact*: "سنڌو ندي زراعت لاءِ اهم وسيلو آهي."
*Generated Instruction*:
•⁠ 	Instruction: وضاحت ڪريو ته سنڌو ندي زراعت لاءِ ڇو اهم آهي؟
•⁠ 	Input: "سنڌو ندي زراعت لاءِ اهم وسيلو آهي."
•⁠ 	Output: "ڇو ته نديءَ جو پاڻي زراعت کي پاڻي مهيا ڪري ٿو، جيڪو پوک لاءِ ضروري آهي."

---

 Example 2 — Commonsense Reasoning

*Fact*: " "پاڻي تي ڄمي ڀو °C 0"
*Generated Instruction*:
•⁠       Instruction: عام فهم جي بنياد تي ٻڌايو ته جيڪڏهن پاڻي کي 0°C کان گھٽ ٿڌو ڪيو وڃي ته ڇا ٿيندو؟
•⁠	Input: "پاڻي 0°C تي ڄمي ٿو."
•⁠	Output: "پاڻي برف ۾ تبديل ٿي ويندو."

---

 Output Format (in JSON):

```json
{
  "Inductive Reasoning": {
    "Instruction": "Sindhi Instruction",
    "Input": "Sindhi Input",
    "Output": "Sindhi Output"
  },
  "Deductive Reasoning": {
    "Instruction": "Sindhi Instruction",
    "Input": "Sindhi Input",
    "Output": "Sindhi Output"
  }
}

Use the following fact to generate both Causal and Commonsense reasoning tasks:
'''

# ---------- Define functions for Gradio ----------

def generate_output(user_input_text):
    """
    Combines the fixed prompt with the user's input,
    calls the generate() function and returns the generated Sindhi output.
    """
    full_prompt = f"{fixed_prompt}{user_input_text}"
    sindhi_generated = generate(api_key, full_prompt, model)
    return sindhi_generated

def save_output(user_input_text, sindhi_output):
    """
    Saves the provided user input and generated (or edited) Sindhi JSON output to a CSV file.
    It parses the JSON output (after cleaning any markdown artifacts), then stores each reasoning type
    along with the original user input. If the CSV file already exists, the new records get appended.
    """
    # Clean the output from any markdown formatting, if present.
    cleaned = sindhi_output.replace("json\n", "").replace("```", "")
    
    try:
        output_dict = json.loads(cleaned)
    except Exception as e:
        return f"Error parsing JSON: {e}"

    # Each reasoning type will become a row; we include the original user input as an extra column.
    rows = []
    for reasoning_type, details in output_dict.items():
        row = {
            "User Input": user_input_text,
            "Reasoning Type": reasoning_type,
            "Instruction": details.get("Instruction", ""),
            "Input": details.get("Input", ""),
            "Output": details.get("Output", "")
        }
        rows.append(row)
    df_new = pd.DataFrame(rows)
    
    csv_filename = "output_sindhi.csv"
    if os.path.exists(csv_filename):
        # Read the existing CSV and append the new records
        df_existing = pd.read_csv(csv_filename)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new

    try:
        df_final.to_csv(csv_filename, index=False)
    except Exception as e:
        return f"Error saving CSV: {e}"
        
    return f"Data successfully saved to {csv_filename}."

# ---------- Gradio Interface ----------
with gr.Blocks() as demo:
    gr.Markdown("## Sindhi Text Generation and CSV Save")
    
    with gr.Column():
        user_input = gr.Textbox(label="User Input Text",
                                placeholder="Enter your Sindhi text here ...",
                                lines=10)
                                
                                
        generate_btn = gr.Button("Generate Sindhi Output")
        sindhi_output = gr.Textbox(label="Sindhi Output (editable)",
                                   placeholder="The generated output will appear here...",
                                   lines=15)
        
    with gr.Row():
        save_btn = gr.Button("Save Output to CSV")
        status_output = gr.Textbox(label="Status", interactive=False)
    
    # When "Generate" is clicked, run generate_output() using the text from the user input.
    generate_btn.click(fn=generate_output,
                       inputs=user_input,
                       outputs=sindhi_output)
    
    # When "Save" is clicked, run save_output() with both the user input and
    # the (possibly edited) sindhi_output text.
    save_btn.click(fn=save_output,
                   inputs=[user_input, sindhi_output],
                   outputs=status_output)

# Launch the app
demo.launch()

