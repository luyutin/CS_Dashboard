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
- `process/media_cleaner/`: unknown Excel cleaning engine and editable text configuration
- `Report Template & All Format 字典.xlsx`: default field dictionary
- `Photos/`: images used by the upload instructions

Customer workbooks, local outputs, virtual environments, generated executables,
and legacy project copies are intentionally excluded from Git.

### Unknown-data formatter maintenance

The cleaner is a package under `process/media_cleaner/`. Its Python API is in
`engine.py`; editable aliases, field descriptions, and Ollama prompts are under
`process/media_cleaner/config/`. The canonical field names and order come from
`process/template.py::template()`. Completely empty columns are omitted from
each output workbook. Restart Streamlit after changing these text files.

On the Streamlit page, each uploaded workbook shows its worksheet names. Only
the first worksheet is selected by default; users can explicitly include more.
Selected worksheets are detected and audited independently, then merged into
the workbook's cleaned output. Source file and worksheet remain traceable in
the audit worksheets.

The standalone CLI is:

```bash
python -m process.media_cleaner input.xlsx --no-ollama
```

## Update an existing Windows installation

For a source-code installation, close the running dashboard, open PowerShell in
the project directory, then run:

```powershell
git pull origin main
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_main.py
```

If the user runs a packaged `.exe`, pulling the repository does not update that
executable. Rebuild it on Windows from the latest `main` branch and replace the
old distribution. The build must include both `Report Template & All Format
字典.xlsx` and the entire `process/media_cleaner/config` directory.

## Building a Windows executable

Build the executable on Windows after installing the dependencies. Ollama and the
model remain separate prerequisites and are not embedded in the executable. Ensure
the field dictionary, Streamlit static assets, and the complete
`process/media_cleaner/config` directory are included in the PyInstaller configuration.
