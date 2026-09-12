# CS4360 Senior Experience Project

## Network Anomaly Detection and Automated Threat Analysis

This project uses statistical and machine-learning methods to detect unusual network behavior. The initial development and testing uses the NSL-KDD dataset.

## Requirements

Before running the project, make sure the following are installed:

- Python 3
- Git
- Visual Studio Code
- Python extension for Visual Studio Code

## Clone the Repository

Clone the project and enter the project directory:

```powershell
git clone https://github.com/TommyLenot/CS4360-Senior-Experience-Project.git
cd CS4360-Senior-Experience-Project
```

## Create a Python Virtual Environment

From the project directory:

```powershell
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell prevents the environment from activating, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

When the environment is active, the terminal should begin with:

```text
(.venv)
```

## Install Python Dependencies

The Python packages used by the project are stored in `requirements.txt`.

With the virtual environment active, run:

```powershell
python -m pip install -r requirements.txt
```

This installs the packages currently used by the project, including tools for:

- Data processing
- Machine learning
- Statistical analysis
- Visualization
- Jupyter notebooks
- Streamlit
- Automated testing with pytest

## NSL-KDD Dataset

The raw NSL-KDD dataset is **not stored in this GitHub repository**.

The `data/raw/` directory is excluded through `.gitignore`, so each team member needs to download the dataset separately.

Download these two files:

```text
KDDTrain+.txt
KDDTest+.txt
```

NSL-KDD dataset mirror:

https://github.com/Jehuty4949/NSL_KDD

After downloading the files, place them here:

```text
CS4360-Senior-Experience-Project/
│
├── data/
│   └── raw/
│       ├── KDDTrain+.txt
│       └── KDDTest+.txt
│
├── notebooks/
├── src/
├── tests/
├── requirements.txt
└── README.md
```

Do not rename the dataset files because the project currently expects these filenames.

## Running the Jupyter Notebook

Open:

```text
notebooks/eda_nsl_kdd.ipynb
```

Select the project's virtual environment as the Jupyter kernel:

```text
.venv (Python)
```

Run the notebook cells from top to bottom.

The notebook currently contains:

- NSL-KDD data loading
- Exploratory data analysis
- Normal vs. attack distribution
- Feature distributions
- Correlation analysis
- Data preprocessing
- Isolation Forest baseline
- Confusion matrix
- Precision, recall, and F1 evaluation
- Anomaly score generation

## Running Tests

From the project root with `.venv` activated:

```powershell
python -m pytest -v
```

The current tests verify:

- Feature and label separation
- NSL-KDD preprocessing
- Training/test preprocessing compatibility
- Isolation Forest compatibility

## Current Project Structure

```text
CS4360-Senior-Experience-Project/
│
├── data/
│   └── raw/
│
├── notebooks/
│   └── eda_nsl_kdd.ipynb
│
├── src/
│   ├── agent/
│   ├── dashboard/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── preprocessing.py
│   └── detection/
│
├── tests/
│   ├── test_preprocessing.py
│   └── test_isolation_forest_compatibility.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

### Week 1

- Project environment and repository setup
- NSL-KDD data loading
- Exploratory data analysis
- Dataset distribution and feature analysis

### Week 2

- Reusable preprocessing pipeline
- Binary normal/attack labels
- Categorical feature encoding
- Numerical feature scaling
- Train/test preprocessing
- Automated preprocessing tests
- Isolation Forest compatibility testing
- Isolation Forest baseline
- Confusion matrix
- Precision, recall, and F1 evaluation
- Anomaly scores

## Important Notes

Do not commit:

- `.venv/`
- Python cache files
- pytest cache files
- Raw NSL-KDD dataset files

These files are intentionally excluded through `.gitignore`.

If new Python packages are installed for the project, update `requirements.txt` so the rest of the team can install the same dependencies.