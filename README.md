# Set Up Virtual Environment
   **Create virtual environment On macOS/Linux:**
```
python3 -m venv env
source env/bin/activate
```
**Create virtual environment On Windows:**
```
python -m venv env
venv\Scripts\activate
```
**Install Dependencies**
```
pip install -r requirements.txt
```

## Using github 
Environment:
```
GEMINI_API_KEY=api_key
GITHUB_REPO_BASE = "https://api.github.com/repos/username/repository_name"  
```
then run:
```
python final_github_md_file.py
```

# CrewAI

**To Run CrewAI**

```
cd agentic_parser
then run any python file
```

```
to read the md file from local
create new docs folder in this directory and add the md files then run localmd.py
```

# Run Mkdocs

**Serve the Documentation Locally**
```
mkdocs serve
```

**documentation will be live at:**
```
https://documentation-using-ai-agent.readthedocs.io/en/latest/
```
