# CS4360 Senior Experience Project

## Network Anomaly Detection and Automated Threat Analysis

This project uses statistical and machine-learning methods to detect unusual network behavior. The initial development and testing uses the NSL-KDD dataset.

The project is designed to learn patterns of normal network behavior and identify records that deviate from those patterns. Detected anomalies can later be passed to an AI-assisted investigation component for additional analysis and explanation.

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
|
+-- data/
|   +-- raw/
|       +-- KDDTrain+.txt
|       +-- KDDTest+.txt
|
+-- notebooks/
+-- src/
+-- tests/
+-- requirements.txt
+-- README.md
```

Do not rename the dataset files because the data preparation pipeline expects these filenames.

The current NSL-KDD files contain:

```text
Training records: 125,973
Test records:      22,544
Raw columns:       43
```

The 43 raw columns consist of the network features along with the attack label and difficulty field.

## Prepare the Dataset

The project contains a reusable data preparation pipeline. This allows team members to generate model-ready data without running preprocessing manually through the Jupyter notebook.

From the project root, with `.venv` activated, run:

```powershell
python -m src.data.prepare_data
```

The pipeline performs the following steps:

1. Checks that `KDDTrain+.txt` and `KDDTest+.txt` exist.
2. Loads the NSL-KDD training and test datasets.
3. Separates the network features from the labels and difficulty field.
4. Converts the labels to binary values:
   - `0` = normal
   - `1` = attack
5. One-hot encodes categorical features:
   - `protocol_type`
   - `service`
   - `flag`
6. Standardizes numerical features.
7. Removes zero-variance features using `VarianceThreshold`.
8. Applies the preprocessing learned from the training set to the test set.
9. Validates the processed data.
10. Saves the processed datasets and fitted preprocessor.

A successful run currently produces:

```text
Training shape:           (125973, 43)
Test shape:               (22544, 43)
Processed training shape: (125973, 121)
Processed test shape:     (22544, 121)
```

The preprocessing pipeline is fit using the training data. The fitted preprocessing transformations are then applied to the test data so that the training and test datasets use the same feature space.

## Processed Data Validation

Before the processed data is saved, the pipeline verifies that:

- Training features and labels have matching row counts.
- Test features and labels have matching row counts.
- Training and test data have the same number of features.
- Processed features are numeric.
- Processed features contain no NaN values.
- Processed features contain no infinite values.
- Training labels contain only `0` and `1`.
- Test labels contain only `0` and `1`.

The preprocessing pipeline also automatically removes features with zero variance.

During development, `num_outbound_cmds` was identified as a zero-variance NSL-KDD feature. The pipeline removes zero-variance features automatically rather than hard-coding a specific column.

## Generated Processed Files

Running:

```powershell
python -m src.data.prepare_data
```

creates the following files inside `data/processed/`:

```text
data/processed/
|
+-- X_train_processed.joblib
+-- X_test_processed.joblib
+-- y_train.joblib
+-- y_test.joblib
+-- preprocessor.joblib
```

These files are generated artifacts and do not need to be manually edited.

The processed feature matrices currently contain 121 model-ready features.

## Loading Processed Data for Detection Models

Team members working on detection models can load the prepared data directly instead of repeating the preprocessing process.

Example:

```python
from src.data.preprocessing import load_processed_data

(
    X_train,
    X_test,
    y_train,
    y_test,
    preprocessor
) = load_processed_data()
```

The returned objects are:

```text
X_train      -> processed training features
X_test       -> processed test features
y_train      -> binary training labels
y_test       -> binary test labels
preprocessor -> fitted preprocessing pipeline
```

`X_train` and `X_test` are numeric NumPy arrays containing finite values.

The processed data has been compatibility-tested with:

- Isolation Forest
- Logistic Regression
- Random Forest

These compatibility tests verify that the preprocessing/data pipeline can successfully provide input to the models. They do not replace the full model training, tuning, or statistical evaluation performed by the detection component.

## Mahalanobis Distance Data Note

The Week 3 detection work includes Mahalanobis distance.

The processed data is numeric, finite, and contains no zero-variance features. During data-pipeline testing, a 10,000-row training sample containing all 121 processed features had a matrix rank of 110.

This means some processed dimensions are linearly dependent. The data pipeline does not automatically remove these additional dimensions because doing so would make a modeling decision on behalf of the detection component.

The Mahalanobis implementation should therefore account for the possibility of a singular or near-singular covariance matrix.

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
python -m pytest tests -v
```

The current automated test suite contains 15 tests.

The tests verify:

- Feature and label separation
- NSL-KDD preprocessing
- Training/test preprocessing compatibility
- Processed-data validation
- Rejection of row-count mismatches
- Rejection of feature-count mismatches
- Rejection of NaN and infinite feature values
- Rejection of invalid binary labels
- Processed-data saving and loading
- Saved model-data handoff
- Isolation Forest compatibility
- Logistic Regression compatibility
- Random Forest compatibility

The current verified result is:

```text
15 passed
```

## Current Project Structure

```text
CS4360-Senior-Experience-Project/
|
+-- data/
|   +-- processed/
|   |   +-- .gitkeep
|   |   +-- generated .joblib files
|   |
|   +-- raw/
|       +-- KDDTrain+.txt
|       +-- KDDTest+.txt
|
+-- notebooks/
|   +-- eda_nsl_kdd.ipynb
|
+-- src/
|   +-- agent/
|   +-- dashboard/
|   +-- data/
|   |   +-- __init__.py
|   |   +-- loader.py
|   |   +-- prepare_data.py
|   |   +-- preprocessing.py
|   |
|   +-- detection/
|
+-- tests/
|   +-- test_data_validation.py
|   +-- test_isolation_forest_compatibility.py
|   +-- test_model_data_handoff.py
|   +-- test_preprocessing.py
|   +-- test_processed_data_io.py
|   +-- test_supervised_model_compatibility.py
|
+-- .gitignore
+-- README.md
+-- requirements.txt
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

### Week 3 - Data/DevOps

- Added a terminal-runnable data preparation pipeline.
- Added reusable processed-data saving and loading.
- Added validation for processed model data.
- Added missing raw-dataset checks.
- Added numeric and finite-value validation.
- Added binary-label validation.
- Added automatic zero-variance feature removal.
- Reduced the processed feature space from 122 to 121 features by removing a zero-variance feature.
- Added saved-data handoff testing.
- Verified Isolation Forest compatibility.
- Verified Logistic Regression compatibility.
- Verified Random Forest compatibility.
- Investigated matrix properties relevant to the Mahalanobis distance handoff.
- Expanded the automated test suite to 15 passing tests.

The Week 3 Data/DevOps work prepares a reusable model-data interface for the detection work while leaving model implementation, tuning, and statistical comparison to the detection component.

## Important Notes

Do not commit:

- `.venv/`
- Python cache files
- pytest cache files
- Raw NSL-KDD dataset files
- Generated processed `.joblib` files

These files should remain excluded through `.gitignore`.

If the generated processed files are not present after cloning the repository, place the NSL-KDD files in `data/raw/` and run:

```powershell
python -m src.data.prepare_data
```

This will regenerate the processed data locally.

If new Python packages are installed for the project, update `requirements.txt` so the rest of the team can install the same dependencies.