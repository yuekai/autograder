# Yuekai's autograder

---

## Getting started

### 🛠️ Environment setup

- 💡 To use the `o4-mini` version, make sure you have the latest `openai` package installed.
- 📦 Install only what you need:
  - For OpenAI API: `openai`
  - ~~For open-source models: `vllm`~~


```bash
pip install openai 
```

### 📄 Convert PDF to JSON

1. Clone the `s2orc-doc2json` repository to convert your PDF file into a structured JSON format.  
   (For detailed configuration, please refer to the [official repository](https://github.com/allenai/s2orc-doc2json).)

```bash
git clone https://github.com/yuekai/s2orc-doc2json.git
```

2. Start the PDF processing service.

```bash
cd ./s2orc-doc2json/grobid-0.7.3
./gradlew run
```

3. Convert your PDF into JSON format.
To convert a single PDF file to JSON, pass the path of the file as the `-i` argument to `process_pdf.py`

```bash
python ./s2orc-doc2json/doc2json/grobid2json/process_pdf.py
```
To convert all the PDF files in a directory to JSON, pass the directory as as the `-i` argument to `process_pdf.py`
```bash
python ./s2orc-doc2json/doc2json/grobid2json/process_pdf.py -i ${PDF_DIR}
```

### 🚀 Running the autograder
Modify `SUBMISSIONS_DIR` variables in `autograder.sh` to point to the directory containing the PDF files to grade. Run the `autograder.sh` script to grade the submissions.
```bash
export OPENAI_API_KEY="<OPENAI_API_KEY>"
./autograder.sh
```