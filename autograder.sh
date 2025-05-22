#!/bin/zsh

# CONFIGURATION
GPT_VERSION="o4-mini"
SUBMISSIONS_DIR="/Users/yuekai/Downloads/ungraded" 

# Check if the target directory exists
if [ ! -d "$SUBMISSIONS_DIR" ]; then
  echo "Error: Directory '$SUBMISSIONS_DIR' not found."
  exit 1
fi

# Loop through all files ending in .pdf in the submissions directory
for json_path in "$SUBMISSIONS_DIR"/*.pdf.json; do

  # Check if the glob found any files (otherwise json_path may be "*.pdf.json")
  [ -e "$json_path" ] || continue

  clean_json_path="${json_path%.pdf.json}.json"

  echo "Grading submission: $json_path"

  # Execute autograding scripts
  python clean_json.py \
      --input_json_path ${json_path} \
      --output_json_path ${clean_json_path}
  
  python grading.py \
      --gpt_version ${GPT_VERSION} \
      --pdf_json_path ${clean_json_path} \
      --output_dir ${SUBMISSIONS_DIR}

done

exit 0