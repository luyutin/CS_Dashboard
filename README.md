# Media Report Dashboard & ROI Modeller+

Streamlit dashboard for formatting media reports, cleaning unknown Excel layouts,
and running ROI analysis. The unknown-data formatter can use a local Ollama model
to assist with header detection and automatically falls back to deterministic rules
when Ollama is unavailable.

## Requirements

- Python 3.11
- Ollama (optional, recommended for unknown Excel layouts)
- Ollama model `qwen3.5:9b` (about 6.6 GB)

## Set up on another computer

Clone this repository, open a terminal in the project directory, and create a new
virtual environment. Do not copy `.venv` from another computer.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For AI-assisted header detection, install Ollama from its official website and run:

```bash
ollama pull qwen3.5:9b
```

Ollama normally exposes its local API at `http://127.0.0.1:11434`. The application
still works in rule-only mode if Ollama is not installed or the option is disabled.

## Run

```bash
python run_main.py
```

Alternatively:

```bash
streamlit run main.py
```

## Repository contents

- `main.py`: Streamlit navigation and page entry points
- `process/`: dashboard pages and media-specific formatters
- `clean_media_data.py`: unknown Excel detection and cleaning engine
- `Report Template & All Format 字典.xlsx`: default field dictionary
- `Photos/`: images used by the upload instructions

Customer workbooks, local outputs, virtual environments, generated executables,
and legacy project copies are intentionally excluded from Git.

## Building a Windows executable

Build the executable on Windows after installing the dependencies. Ollama and the
model remain separate prerequisites and are not embedded in the executable. Ensure
the field dictionary and Streamlit static assets are included in the PyInstaller
configuration.
