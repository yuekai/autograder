from openai import OpenAI
import json
from tqdm import tqdm
import argparse
import os
from utils import print_response, print_log_cost, load_accumulated_cost, save_accumulated_cost

parser = argparse.ArgumentParser()

parser.add_argument('--gpt_version',type=str)
parser.add_argument('--pdf_json_path', type=str) # json format
parser.add_argument('--output_dir',type=str, default=None)

args    = parser.parse_args()

client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

gpt_version = args.gpt_version
pdf_json_path = args.pdf_json_path
output_dir = args.output_dir
if output_dir is None:
    output_dir = os.path.dirname(pdf_json_path)

with open(f'{pdf_json_path}') as f:
    report_json = json.load(f)

intro_msg = [
        {'role': "system", "content": f"""You are a teaching assistant for a graduate level optimization course in a statistics department. 
You will receive a student's project report. 
Your task is to critique the report according to the project guidelines. 
Focus on how the report falls short of the project guidelines because our goal is to help the students identify ways to improve their report.

Here is the project report in JSON format:
{report_json}"""},
        {"role": "user",
         "content" : """Please critique the introduction section of the report. According to the project guidelines, the introduction section should: 

* Explain the problem and why it is important; 
* Clearly state what the inputs and outputs of the machine learning problem are."""}
]

related_work_msg = [
        {"role": "user", "content": """Please critique the related work section of the report. According to the project guidelines, the related work section should find relevant papers, group them into categories based on their approaches, discuss their strengths and weaknesses, and compare them with the approach in the project."""}
]

dataset_msg = [
        {"role": "user", "content": """Please critique the dataset and features section of the report. According to the project guidelines, the dataset and features section should:

* Describe the dataset the project uses;
* How many training/validation/test examples does the dataset contain?
* Was the data preprocessed in any way? 
* What features were extracted?"""}
]

methods_msg = [
        {"role": "user", "content": """Please critique the methods section. According to the project guidelines, the methods section should:

* Describe the machine learning pipeline, including any algorithm(s). Make sure to include relevant mathematical details. 
* For each algorithm, give a short description (1 to 2 paragraphs) of how it works. If the algorithm is cutting edge or niche (or any algorithm not covered in class), provide enough detail so that the class can understand the algorithm. 
* describe how (hyper)parameters were chosen (e.g. what was the mini-batch size and why)."""}
]

results_msg = [
        {"role": "user", "content": """Please critique the experiments/results section of the report. According to the project guidelines, the experiments/results section should:

* present the results with a mixture of tables and plots. For example, if the project solves a classification problem, this section should include a confusion matrix or AUC/AUPRC curves. 
* The figures should include legends, axis labels, and have font sizes that are legible when printed. 
* describe (mathematically if necessary) any metrics the section reports and refer to any figures/tables in the main text. 

The section should have both quantitative and qualitative results."""}
]

conclusion_msg = [
        {"role": "user", "content": """Please critique the conclusion section. According to the project guidelines, the conclusion section should:

* Summarize the report and reiterate the main points. What worked and what didn’t work (and why)? 
* Discuss the advantages and disadvantages of your method (e.g. provide examples of where the algorithm failed/succeeded). 
* For future work, how can the method be improved?"""}
]

# config
overall_msg = [
        {'role': 'user', 'content': """Please summarize weaknesses of all the sections and assess the following aspects of the report:

1. overall technical depth/merit: How technically challenging was what you did? If you are working with a well-studied dataset, then we expect you to achieve close to state-of-the-art performance.
2. breadth/scope: How broad was your project? How many aspects, angles, variations did you explore?
3. clarity: How well did you explain what you did, your results, and interpret the outcomes? Did you use the good graphs and visualizations? How clear was the writing?"""}
]

def api_call(msg, gpt_version):
    if "o3-mini" in gpt_version or "o4-mini" in gpt_version:
        completion = client.chat.completions.create(
            model=gpt_version, 
            reasoning_effort="high",
            messages=msg
        )
    else:
        completion = client.chat.completions.create(
            model=gpt_version, 
            messages=msg
        )

    return completion 

responses = []
trajectories = []
total_accumulated_cost = 0

for idx, instruction_msg in enumerate([intro_msg, related_work_msg, dataset_msg, methods_msg, results_msg, conclusion_msg, overall_msg]):
    current_stage = ""
    if idx == 0 :
        current_stage = f"[Grading] Introduction"
    elif idx == 1:
        current_stage = f"[Grading] Related work"
    elif idx == 2:
        current_stage = f"[Grading] Dataset and features"
    elif idx == 3:
        current_stage = f"[Grading] Methods"
    elif idx == 4:
        current_stage = f"[Grading] Results"
    elif idx == 5:
        current_stage = f"[Grading] Conclusion"
    elif idx == 6:
        current_stage = f"[Grading] Overall"
    print(current_stage)

    trajectories.extend(instruction_msg)

    completion = api_call(trajectories, gpt_version)
    
    # response
    completion_json = json.loads(completion.model_dump_json())

    # print and logging
    # print_response(completion_json)
    if idx == 6:
        temp_total_accumulated_cost = print_log_cost(completion_json, gpt_version, current_stage, output_dir, total_accumulated_cost)
    else:
        temp_total_accumulated_cost = print_log_cost(completion_json, gpt_version, current_stage, output_dir, total_accumulated_cost, verbose=False)
    total_accumulated_cost = temp_total_accumulated_cost

    responses.append(completion_json)

    # trajectories
    message = completion.choices[0].message
    trajectories.append({'role': message.role, 'content': message.content})


# save
# save_accumulated_cost(f"{output_dir}/accumulated_cost.json", total_accumulated_cost)

# os.makedirs(output_dir, exist_ok=True)

# with open(f'{output_dir}/planning_response.json', 'w') as f:
#     json.dump(responses, f)

# with open(f'{output_dir}/planning_trajectories.json', 'w') as f:
#     json.dump(trajectories, f)

report_name_sans_ext = os.path.splitext(os.path.basename(pdf_json_path))[0]
output_path = os.path.join(output_dir, f"{report_name_sans_ext}_comments.md")
with open(output_path, 'w') as f:
    f.write(print_response(completion_json))
