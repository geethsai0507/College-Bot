# College-Bot
AI powered college chatbot using RAG
Collecting workspace informationGitHub Copilot

Here’s a concise GitHub project description you can use for your chatbot repo.

Project title
AI-Powered Faculty Chatbot

Short description
A local chatbot that indexes faculty data and PDFs, generates embeddings, and answers queries via a simple web UI and command-line tools.

Key features
- Ingests faculty CSVs and PDFs and converts them to JSON and embeddings. See faculty_data.csv and faculty_data.json.  
- Text extraction and preprocessing utilities: convert_csv.py, extract_teacher.py, extract.py, models.py.  
- Embedding and index building: get_embedding_function_copy.py, populate_database_copy.py, index stored at index.faiss.  
- Query and demo tools: quer.py, main.py.  
- Web UI and server: backend app.py, frontend base.html, app.js, style.css.  
- Config and models: config.py, chatmodel.txt, zrok.txt. Logs and examples in logs.

Quick start
1. Install dependencies:
```sh
pip install -r mini/requirements.txt
```
(see mini/requirements.txt)

2. Populate the index (if needed) using:
- get_embedding_function_copy.py and
- populate_database_copy.py

3. Run the web app:
```sh
python app.py
```
(See the UI in base.html and static/app.js.)

Why this repo
- Integrates document extraction, embedding creation, and a FAISS index for fast retrieval.  
- Simple web UI plus CLI tools for experiments and debugging.

Files to inspect first
- app.py — main server  
- extract.py — data extraction pipeline  
- get_embedding_function_copy.py — embedding helper  
- populate_database_copy.py — index builder  
- index.faiss — prebuilt index

Use or adapt this description in your repository README.