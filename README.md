# CS4360 Senior Experience Project

## Network Anomaly Detection and Automated Threat Analysis

This project uses statistical and machine-learning methods to detect unusual network behavior.

Initial development and testing used the NSL-KDD dataset. The project now also supports the CICIDS2017 dataset for additional detection development and evaluation.

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


# NSL-KDD Data Pipeline

## NSL-KDD Dataset

The raw NSL-KDD dataset is **not stored in this GitHub repository**.

The `data/raw/` directory is excluded through `.gitignore`, so each team member needs to download the dataset separately.

Download these two files:

```text
KDDTrain+.txt
KDDTest+.txt
```

NSL-KDD dataset mirror:

```text
https://github.com/Jehuty4949/NSL_KDD
```

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
Test records:       22,544
Raw columns:            43
```

The 43 raw columns consist of the network features along with the attack label and difficulty field.


## Prepare the NSL-KDD Dataset

The project contains a reusable NSL-KDD data preparation pipeline. This allows team members to generate model-ready data without running preprocessing manually through the Jupyter notebook.

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
Test shape:                (22544, 43)
Processed training shape: (125973, 121)
Processed test shape:      (22544, 121)
```

The preprocessing pipeline is fit using the training data. The fitted preprocessing transformations are then applied to the test data so that the training and test datasets use the same feature space.


## NSL-KDD Processed Data Validation

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


## NSL-KDD Generated Processed Files

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

The processed NSL-KDD feature matrices currently contain 121 model-ready features.


## Loading NSL-KDD Processed Data

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

- Logistic Regression
- Random Forest

These compatibility tests verify that the preprocessing/data pipeline can successfully provide input to the models. They do not replace the full model training, tuning, or statistical evaluation performed by the detection component.


## Mahalanobis Distance Data Note

The Week 3 detection work includes Mahalanobis distance.

The processed NSL-KDD data is numeric, finite, and contains no zero-variance features. During data-pipeline testing, a 10,000-row training sample containing all 121 processed features had a matrix rank of 110.

This means some processed dimensions are linearly dependent. The data pipeline does not automatically remove these additional dimensions because doing so would make a modeling decision on behalf of the detection component.

The Mahalanobis implementation should therefore account for the possibility of a singular or near-singular covariance matrix.


## Running the NSL-KDD Jupyter Notebook

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


# CICIDS2017 Data Pipeline

## CICIDS2017 Dataset

Week 4 adds CICIDS2017 as an additional network intrusion dataset.

The raw CICIDS2017 files are **not stored in this GitHub repository**. The files are kept under `data/raw/`, which is excluded through `.gitignore`.

The project currently uses the eight MachineLearningCSV files:

```text
Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
Friday-WorkingHours-Morning.pcap_ISCX.csv
Monday-WorkingHours.pcap_ISCX.csv
Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
Tuesday-WorkingHours.pcap_ISCX.csv
Wednesday-workingHours.pcap_ISCX.csv
```

Place the files in:

```text
data/raw/cicids2017/MachineLearningCVE/
```

The CICIDS2017 machine-learning CSV files contain 79 columns:

```text
78 network-flow features
1 attack label
```

Unlike NSL-KDD, these files already contain numeric model features and therefore do not require one-hot encoding.

The available features include `Destination Port` and network-flow statistics. The MachineLearningCSV files used by this project do not contain source or destination IP address columns.


## CICIDS2017 Loading and Cleaning

CICIDS2017 loading is handled by:

```text
src/data/cicids_loader.py
```

The loader:

1. Locates the CICIDS2017 CSV files.
2. Loads each CSV using pandas.
3. Removes leading and trailing whitespace from column names.
4. Cleans attack-label text.
5. Converts positive and negative infinity values to NaN.
6. Removes records with invalid `Flow Bytes/s` or `Flow Packets/s` values.
7. Supports combining the cleaned CSV files when needed.

After cleaning all eight files, the dataset contains:

```text
Total cleaned records: 2,827,876
```

During cleaning, approximately 0.10% of the original records were removed because they contained invalid flow-rate values.

Duplicate network-flow records are not automatically removed. Repeated network flows may represent legitimate repeated observations, and removing them would change the dataset distribution. Duplicate handling is therefore not performed automatically by the data-loading pipeline.


## CICIDS2017 Label Distribution

The cleaned dataset contains both benign traffic and multiple attack categories.

The binary distribution is:

```text
BENIGN: 2,271,320 (80.3189%)
ATTACK:   556,556 (19.6811%)
```

The attack categories include:

- DoS Hulk
- PortScan
- DDoS
- DoS GoldenEye
- FTP-Patator
- SSH-Patator
- DoS slowloris
- DoS Slowhttptest
- Bot
- Web Attack - Brute Force
- Web Attack - XSS
- Infiltration
- Web Attack - Sql Injection
- Heartbleed

Some attack categories contain very few records. The data preparation process therefore preserves the original attack labels in addition to producing binary benign/attack labels.


## CICIDS2017 Diagnostic Scripts

Three diagnostic scripts are included for inspecting the CICIDS2017 data:

```text
check_cicids_schema.py
check_cicids_variance.py
check_cicids_labels.py
```

### Schema Check

Run:

```powershell
python check_cicids_schema.py
```

The schema check verifies that all eight CSV files contain the same columns.

The current verified result is:

```text
Files checked: 8
Columns per file: 79
All schemas match: True
```

### Variance Check

Run:

```powershell
python check_cicids_variance.py
```

The variance diagnostic checks which CICIDS2017 model features vary across the complete set of files.

The current result is:

```text
Total features: 78
Features that vary: 70
Constant across all files: 8
```

The eight globally constant features are:

```text
Bwd Avg Bulk Rate
Bwd Avg Bytes/Bulk
Bwd Avg Packets/Bulk
Bwd PSH Flags
Bwd URG Flags
Fwd Avg Bulk Rate
Fwd Avg Bytes/Bulk
Fwd Avg Packets/Bulk
```

These features are removed automatically during preprocessing using `VarianceThreshold`.

### Label Check

Run:

```powershell
python check_cicids_labels.py
```

This script calculates the cleaned label distribution across all eight CICIDS2017 files and reports both the original attack categories and the combined benign/attack distribution.


## Prepare the CICIDS2017 Dataset

The reusable CICIDS2017 preparation script is:

```text
src/data/prepare_cicids_data.py
```

From the project root, with `.venv` activated, run:

```powershell
python -m src.data.prepare_cicids_data
```

The preparation process:

1. Locates all eight CICIDS2017 CSV files.
2. Loads and cleans each file.
3. Adds the originating CSV filename as temporary metadata.
4. Creates reproducible training and test partitions.
5. Uses an 80/20 split with `random_state=42`.
6. Stratifies each file using the original CICIDS2017 attack labels.
7. Combines the training partitions.
8. Combines the test partitions.
9. Separates model features from labels and source-file metadata.
10. Creates binary labels:
    - `0` = BENIGN
    - `1` = ATTACK
11. Preserves the original attack-type labels separately.
12. Removes zero-variance features using `VarianceThreshold`.
13. Standardizes the remaining numerical features using `StandardScaler`.
14. Fits preprocessing using only the training data.
15. Applies the fitted preprocessing to the test data.
16. Converts the processed model arrays to `float32`.
17. Validates the final model-ready data.
18. Saves the processed data and fitted preprocessor.


## CICIDS2017 Train/Test Handoff

The current complete CICIDS2017 preparation produces:

```text
Total cleaned records: 2,827,876
Training records:      2,262,296
Test records:            565,580
Original model features:      78
Processed features:           70
```

The binary training distribution is:

```text
BENIGN: 1,817,051
ATTACK:   445,245
```

The binary test distribution is:

```text
BENIGN: 454,269
ATTACK: 111,311
```

Stratification uses the original attack categories rather than only the binary labels. This helps preserve rare attack categories in both partitions.

For example, the rarest current category, Heartbleed, is represented as:

```text
Training: 9
Test:     2
```

The CICIDS2017 preparation pipeline creates non-overlapping training and test partitions within each source file.


## CICIDS2017 Processed Data Validation

Before saving the final model-ready data, the pipeline verifies that:

- Training features and labels have matching row counts.
- Test features and labels have matching row counts.
- Training and test data have the same number of processed features.
- Training features use `float32`.
- Test features use `float32`.
- Processed training features contain only finite values.
- Processed test features contain only finite values.
- Binary training labels contain only `0` and `1`.
- Binary test labels contain only `0` and `1`.

The current validated processed shapes are:

```text
Training: (2262296, 70) float32
Test:     (565580, 70) float32
```

Both arrays have been verified to contain no NaN or infinite values.

The use of `float32` reduces the memory required by the processed feature matrices while retaining the same record and feature counts.


## CICIDS2017 Generated Processed Files

Running:

```powershell
python -m src.data.prepare_cicids_data
```

creates:

```text
data/processed/cicids2017/
|
+-- X_train_processed.joblib
+-- X_test_processed.joblib
+-- y_train.joblib
+-- y_test.joblib
+-- attack_labels_train.joblib
+-- attack_labels_test.joblib
+-- preprocessor.joblib
```

These are generated artifacts and should not be manually edited or committed to the repository.

The two types of labels serve different purposes:

```text
y_train / y_test
    -> binary BENIGN/ATTACK labels

attack_labels_train / attack_labels_test
    -> original CICIDS2017 traffic/attack categories
```

This allows the detection component to perform binary anomaly evaluation while still retaining the original attack category for additional analysis.


## Loading CICIDS2017 Processed Data

The processed CICIDS2017 handoff can be loaded using:

```python
from src.data.cicids_preprocessing import load_processed_data

(
    X_train,
    X_test,
    y_train,
    y_test,
    attack_labels_train,
    attack_labels_test,
    preprocessor
) = load_processed_data()
```

The returned objects are:

```text
X_train
    -> processed training features

X_test
    -> processed test features

y_train
    -> binary training labels

y_test
    -> binary test labels

attack_labels_train
    -> original training traffic/attack labels

attack_labels_test
    -> original test traffic/attack labels

preprocessor
    -> fitted CICIDS2017 preprocessing pipeline
```

The saved handoff has been reloaded and verified successfully.

Current verified values:

```text
X_train: (2262296, 70) float32
X_test:  (565580, 70) float32
Training binary labels: 2,262,296
Test binary labels:       565,580
Training attack labels: 2,262,296
Test attack labels:       565,580
Training finite: True
Test finite:     True
```


# Alert Ingestion and Investigation Handoff Pipeline

## Week 5 Alert Handoff

Week 5 adds a controlled interface between the detection component and the AI-assisted investigation component.

The ingestion pipeline is located in:

```text
src/ingestion/
```

The current pipeline does not perform genuine real-time network traffic processing. It provides a controlled replay and batch-style interface that allows detection results to be converted into standardized alerts and passed to later investigation components.

The current flow is:

```text
Detection Component
        |
        | detection result
        v
    AlertReplay
        |
        v
      Alert
        |
        v
    AlertQueue
        |
        | pending alert
        v
   AlertHandoff
        |
        v
AI Investigation Component
        |
        | verdict, confidence score,
        | explanation
        v
InvestigationResult
        |
        v
    AlertQueue
        |
        v
Completed Alert
```

The detection component, ingestion interface, and AI investigation component remain separate.

The ingestion pipeline does not decide whether an alert is malicious, generate AI confidence scores, or create investigation explanations. It provides the data structures and handoff interfaces needed for those components to communicate.


## Alert Structure

Standardized alerts are defined in:

```text
src/ingestion/alert.py
```

Each alert contains:

```text
alert_id
timestamp
dataset
record_index
anomaly_score
model_prediction
actual_label
attack_type
features
status
```

The required detection-result fields are:

```text
dataset
record_index
anomaly_score
model_prediction
```

The following fields are optional:

```text
actual_label
attack_type
features
```

`actual_label` and `attack_type` represent dataset ground truth used during testing and evaluation. They are kept separate from `model_prediction` and should not be interpreted as information discovered by the anomaly-detection model.

The `features` field allows selected network-record information to accompany an alert. For CICIDS2017 this can include actual available fields such as `Destination Port` and network-flow statistics.

The CICIDS2017 MachineLearningCSV files used by this project do not contain source or destination IP address columns, so the ingestion pipeline does not generate or fabricate IP addresses.

Each alert automatically receives:

- A unique UUID-based `alert_id`
- A UTC timestamp
- An initial status of `pending`

Valid investigation statuses are:

```text
pending
completed
failed
```

These statuses allow later components to distinguish alerts waiting for investigation from successfully completed or failed investigations.


## Alert Queue

Alert storage and state tracking are handled by:

```text
src/ingestion/queue.py
```

The current `AlertQueue` is an in-memory queue used as a simple integration point during development.

It supports:

- Adding alerts
- Retrieving an alert by ID
- Retrieving all alerts
- Retrieving pending alerts
- Marking an alert as completed
- Marking an alert as failed
- Rejecting duplicate alert IDs
- Rejecting invalid alert objects
- Storing an `InvestigationResult` for an alert
- Retrieving a stored investigation result
- Checking whether an alert has an investigation result
- Rejecting results for unknown alerts
- Rejecting duplicate investigation results

When a valid `InvestigationResult` is stored for an existing alert, the queue changes that alert's status from `pending` to `completed`.

The queue stores alerts and investigation results separately and associates them using the alert's unique `alert_id`.

Conceptually:

```text
AlertQueue

_alerts
    alert_id -> Alert

_results
    alert_id -> InvestigationResult
```

This queue is intentionally lightweight and currently exists in memory. It establishes the interface needed by the project without introducing a production message broker or claiming genuine real-time processing.


## Controlled Alert Replay

Controlled alert replay is handled by:

```text
src/ingestion/replay.py
```

`AlertReplay` accepts detection-result records and converts them into standardized `Alert` objects.

A detection result can contain:

```python
{
    "dataset": "CICIDS2017",
    "record_index": 1250,
    "anomaly_score": 0.73,
    "model_prediction": 1,
    "actual_label": 1,
    "attack_type": "DDoS",
    "features": {
        "Destination Port": 80,
        "Flow Duration": 5000
    }
}
```

The replay component validates that the required fields are present, creates an `Alert`, and places the alert into the `AlertQueue`.

Multiple detection results can also be replayed sequentially.

This provides a controlled dataset-replay mechanism for integration and testing. It does not represent live packet capture or genuine real-time network ingestion.

The replay component does not run detection models or the AI investigation agent. Those responsibilities remain separated from the ingestion interface.



## Pending Alert Handoff

Pending-alert handoff is handled by:

```text
src/ingestion/handoff.py
```

`AlertHandoff` provides a simple interface that allows the investigation component to retrieve alerts that are waiting for investigation.

It supports:

- Retrieving the next pending alert
- Retrieving the next pending alert as a dictionary
- Counting pending alerts
- Checking whether pending alerts are available

If the queue contains no pending alerts, the handoff returns `None`.

Alerts with a status of `completed` or `failed` are skipped and are not handed to the investigation component as pending work.

The handoff currently retrieves pending alerts using the order in which they were added to the in-memory queue.

This component does not perform the investigation itself. Its responsibility is only to provide the pending alert to the component responsible for AI-assisted investigation.


## Investigation Result Structure

Investigation results are defined in:

```text
src/ingestion/result.py
```

`InvestigationResult` defines the standardized information that can be returned after an alert has been investigated.

Each investigation result contains:

```text
alert_id
verdict
confidence_score
explanation
completed_at
```

Valid verdicts are:

```text
benign
suspicious
malicious
inconclusive
```

The `alert_id` connects the investigation result to the alert that was investigated.

The `confidence_score` must be a numeric value between:

```text
0.0 and 1.0
```

The investigation confidence score is separate from the anomaly score produced by the detection component.

```text
anomaly_score
    -> produced by the anomaly-detection component

confidence_score
    -> produced by the investigation component
```

Neither value is automatically treated by the ingestion pipeline as the probability that an attack occurred.

The ingestion pipeline does not determine how the investigation confidence score is calculated. The AI investigation component is responsible for generating and evaluating its confidence score.

The `explanation` field contains the investigation component's explanation for its verdict and cannot be empty.

Each result also receives a UTC `completed_at` timestamp unless one is explicitly supplied.

An example investigation result is:

```python
{
    "alert_id": "example-alert-id",
    "verdict": "malicious",
    "confidence_score": 0.85,
    "explanation": (
        "The alert contains network behavior "
        "that requires investigation."
    ),
    "completed_at": "2026-09-19T00:00:00+00:00"
}
```


## Investigation Result Return Path

After the investigation component finishes analyzing an alert, its standardized `InvestigationResult` can be returned to the `AlertQueue`.

The queue verifies that:

- The returned object is an `InvestigationResult`.
- The corresponding `alert_id` exists.
- The alert does not already have an investigation result.

If the result is accepted:

1. The result is stored using its `alert_id`.
2. The corresponding alert is located.
3. The alert status is changed to `completed`.
4. The result can later be retrieved using the same alert ID.

The complete controlled integration path is therefore:

```text
Detection Result
      |
      v
AlertReplay
      |
      v
Alert
      |
      v
AlertQueue
      |
      v
AlertHandoff
      |
      v
AI Investigation Component
      |
      v
InvestigationResult
      |
      v
AlertQueue
      |
      v
Completed Alert
```

This establishes both directions of the detection-to-investigation interface without implementing the AI investigation logic inside the ingestion component.


# Automated Testing

## Running Tests

From the project root with `.venv` activated:

```powershell
python -m pytest -v
```

The current automated test suite contains **89 tests**.

The tests verify:

- NSL-KDD feature and label separation
- NSL-KDD preprocessing
- Training/test preprocessing compatibility
- Processed-data validation
- Rejection of row-count mismatches
- Rejection of feature-count mismatches
- Rejection of NaN and infinite feature values
- Rejection of invalid binary labels
- Processed-data saving and loading
- Saved model-data handoff
- Logistic Regression compatibility
- Random Forest compatibility
- CICIDS2017 feature and label separation
- CICIDS2017 binary label conversion
- CICIDS2017 zero-variance feature removal
- CICIDS2017 train/test preprocessing compatibility
- CICIDS2017 `float32` output
- CICIDS2017 finite-value output
- Alert creation and serialization
- Alert field validation
- Optional ground-truth handling
- Alert queue insertion and retrieval
- Pending alert filtering
- Completed and failed investigation states
- Duplicate alert rejection
- Invalid queue-object rejection
- Controlled detection-result replay
- Required detection-result field validation
- Multiple-alert replay
- Pending-alert handoff
- Pending-alert counting
- Completed-alert handoff filtering
- Failed-alert handoff filtering
- Investigation-result creation and serialization
- Investigation-result alert-ID validation
- Investigation verdict validation
- Investigation confidence-score validation
- Investigation explanation validation
- Investigation completion timestamps
- Investigation-result storage
- Investigation-result retrieval
- Alert/result association using `alert_id`
- Automatic completion after storing a result
- Rejection of results for missing alerts
- Rejection of duplicate investigation results
- Rejection of invalid result objects

The CICIDS2017 automated tests use small synthetic datasets rather than loading the complete processed dataset. This keeps the normal test suite fast and avoids requiring hundreds of megabytes of model data for every test run.

The Week 5 ingestion and handoff tests use small synthetic alerts, detection results, and investigation results. They do not require the full CICIDS2017 dataset or processed model files, which keeps these tests fast and independent of model training or AI investigation.

The current verified result is:

```text
89 passed in 3.49s
```


# Current Project Structure

```text
CS4360-Senior-Experience-Project/
|
+-- data/
|   |
|   +-- processed/
|   |   +-- .gitkeep
|   |   +-- generated NSL-KDD .joblib files
|   |   |
|   |   +-- cicids2017/
|   |       +-- generated CICIDS2017 .joblib files
|   |
|   +-- raw/
|       +-- KDDTrain+.txt
|       +-- KDDTest+.txt
|       |
|       +-- cicids2017/
|           +-- MachineLearningCVE/
|               +-- CICIDS2017 CSV files
|
+-- notebooks/
|   +-- eda_nsl_kdd.ipynb
|
+-- src/
|   |
|   +-- agent/
|   |
|   +-- dashboard/
|   |
|   +-- data/
|   |   +-- __init__.py
|   |   +-- loader.py
|   |   +-- preprocessing.py
|   |   +-- prepare_data.py
|   |   +-- cicids_loader.py
|   |   +-- cicids_preprocessing.py
|   |   +-- prepare_cicids_data.py
|   |
|   +-- detection/
|   |
|   +-- ingestion/
|       +-- __init__.py
|       +-- alert.py
|       +-- handoff.py
|       +-- queue.py
|       +-- replay.py
|       +-- result.py
|
+-- tests/
|   +-- test_alert.py
|   +-- test_alert_handoff.py
|   +-- test_alert_queue.py
|   +-- test_alert_queue_results.py
|   +-- test_alert_replay.py
|   +-- test_cicids_preprocessing.py
|   +-- test_data_validation.py
|   +-- test_investigation_result.py
|   +-- test_model_data_handoff.py
|   +-- test_preprocessing.py
|   +-- test_processed_data_io.py
|   +-- test_supervised_model_compatibility.py
|
+-- check_cicids_labels.py
+-- check_cicids_schema.py
+-- check_cicids_variance.py
+-- .gitignore
+-- README.md
+-- requirements.txt
```


# Current Progress

## Week 1

- Project environment and repository setup
- NSL-KDD data loading
- Exploratory data analysis
- Dataset distribution and feature analysis


## Week 2

- Reusable preprocessing pipeline
- Binary normal/attack labels
- Categorical feature encoding
- Numerical feature scaling
- Train/test preprocessing
- Automated preprocessing tests


## Week 3 - Data/DevOps

- Added a terminal-runnable NSL-KDD data preparation pipeline.
- Added reusable processed-data saving and loading.
- Added validation for processed model data.
- Added missing raw-dataset checks.
- Added numeric and finite-value validation.
- Added binary-label validation.
- Added automatic zero-variance feature removal.
- Reduced the processed feature space from 122 to 121 features by removing a zero-variance feature.
- Added saved-data handoff testing.
- Verified Logistic Regression compatibility.
- Verified Random Forest compatibility.
- Investigated matrix properties relevant to the Mahalanobis distance handoff.
- Expanded the automated test suite to 15 passing tests.

The Week 3 Data/DevOps work prepares a reusable model-data interface for the detection work while leaving model implementation, tuning, and statistical comparison to the detection component.


## Week 4 - Data/DevOps

- Added CICIDS2017 dataset support.
- Added reusable CICIDS2017 CSV loading.
- Added CICIDS2017 column-name and attack-label cleaning.
- Added handling for NaN and infinite flow-rate values.
- Verified all eight CICIDS2017 CSV files use the same 79-column schema.
- Analyzed the overall CICIDS2017 label distribution.
- Added binary BENIGN/ATTACK labels while preserving original attack categories.
- Identified eight features that are constant across all CICIDS2017 files.
- Added automatic zero-variance feature removal.
- Reduced the CICIDS2017 feature space from 78 to 70 model-ready features.
- Added reproducible 80/20 train/test preparation using `random_state=42`.
- Added stratification using the original attack labels.
- Verified rare attack categories remain represented in both training and test data.
- Added numerical feature standardization.
- Added `float32` processed feature arrays to reduce memory usage.
- Added validation for row counts, feature counts, binary labels, data types, NaN values, and infinite values.
- Prepared 2,827,876 cleaned CICIDS2017 records.
- Created a reusable saved-data handoff for the detection component.
- Verified the saved CICIDS2017 handoff can be successfully reloaded.
- Added CICIDS2017 automated preprocessing tests.
- Expanded the complete automated test suite from 15 to 21 passing tests.

The Week 4 Data/DevOps work provides a reusable CICIDS2017 data pipeline and model-data handoff. Detection-model implementation, model tuning, threshold selection, and statistical performance evaluation remain responsibilities of the detection component.


## Week 5 - Data/DevOps

- Added a standardized alert structure for detection-to-investigation handoff.
- Added automatically generated unique alert IDs.
- Added UTC timestamps for generated alerts.
- Added pending, completed, and failed investigation states.
- Kept model predictions separate from dataset ground-truth labels.
- Added optional original attack-type information for evaluation.
- Added support for carrying selected network-record features with an alert.
- Added validation for required alert fields.
- Added an in-memory alert queue for controlled integration testing.
- Added pending-alert retrieval.
- Added completed and failed alert-state handling.
- Added duplicate alert-ID protection.
- Added a controlled detection-result replay component.
- Added support for sequential replay of multiple detection results.
- Added validation for required detection-result fields.
- Added a pending-alert handoff interface for the investigation component.
- Added retrieval of the next pending alert.
- Added dictionary-based pending-alert handoff.
- Added pending-alert counting and availability checks.
- Added filtering so completed and failed alerts are not returned as pending work.
- Added a standardized `InvestigationResult` structure.
- Added investigation verdicts for benign, suspicious, malicious, and inconclusive results.
- Added validation for investigation confidence scores.
- Kept investigation confidence separate from the detection anomaly score.
- Added required investigation explanations.
- Added UTC completion timestamps for investigation results.
- Added storage of investigation results in the alert queue.
- Added retrieval of investigation results using `alert_id`.
- Added protection against results for nonexistent alerts.
- Added protection against duplicate investigation results.
- Added automatic transition from `pending` to `completed` when an investigation result is stored.
- Added 68 automated tests covering the Week 5 alert ingestion, handoff, and investigation-result interface.
- Expanded the complete automated test suite from 21 to 89 passing tests.
- Verified all existing Week 1-4 tests continue to pass.

The Week 5 Data/DevOps work establishes a controlled two-way interface between anomaly detection and AI-assisted investigation. Detection results can be converted into standardized alerts, queued, and handed to the investigation component. Standardized investigation results can then be returned to the queue and associated with the original alert.

The current ingestion pipeline supports dataset replay and batch-style integration testing rather than genuine real-time network traffic processing.

The Data/DevOps components do not generate the AI verdict, calculate the AI investigation confidence score, or produce the investigation explanation. Those responsibilities remain with the AI investigation component.


# Important Notes

Do not commit:

- `.venv/`
- Python cache files
- pytest cache files
- Raw NSL-KDD dataset files
- Raw CICIDS2017 dataset files
- Generated NSL-KDD `.joblib` files
- Generated CICIDS2017 `.joblib` files

These files should remain excluded through `.gitignore`.

If the generated NSL-KDD processed files are not present after cloning the repository, place:

```text
KDDTrain+.txt
KDDTest+.txt
```

inside:

```text
data/raw/
```

and run:

```powershell
python -m src.data.prepare_data
```

If the generated CICIDS2017 processed files are not present, place the eight MachineLearningCSV files inside:

```text
data/raw/cicids2017/MachineLearningCVE/
```

and run:

```powershell
python -m src.data.prepare_cicids_data
```

This will regenerate the processed CICIDS2017 model-data handoff locally.

If new Python packages are installed for the project, update `requirements.txt` so the rest of the team can install the same dependencies.
