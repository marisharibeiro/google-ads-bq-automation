# Google Ads → BigQuery Automation

This repository provides a modular, production-style Python pipeline for extracting Google Ads reporting data and loading it into BigQuery.


The solution supports:

- Multiple Google Ads accounts per brand  
- OAuth2 token refresh  
- Configurable date range logic  
- Asynchronous execution across accounts  
- Automatic delete-and-append into BigQuery  

- **Automated email notifications on success or failure**  
- Clean separation of concerns (settings, collectors, utils, secrets)

This template mirrors real-world multi-market data engineering pipelines used in agencies and enterprise environments.

---

## 📂 Repository Structure

```
.
├── .gitignore
├── config.py
├── platforms / googleads
│   ├── data_collector.py
│   ├── googleads_collector.py
│   ├── helper_functions.py
│   ├── main.py
│   ├── settings.py
│   └── token_functions.py
├── main.py
├── secrets
│   ├── googleads-credentials.example.json
│   └── gmail_credentials.example.json
└── utils
    ├── email.py
    └── helpers.py
```

---

## ✨ Key Features

### 1. Multi-account architecture
Define:
- Brand name
- Multiple accounts per brand  
- Separate BigQuery destinations per brand  
- Fully customizable schemas per table  

### 2. Modularized, production-friendly code
| File | Purpose |
|------|---------|
| `googleads/googleads_collector.py` | Google Ads API logic aggregating data across accounts, PER BRAND |
| `googleads/data_collector.py` | Orchestration, merging, loading|
| `googleads/settings.py` | Configuration for brands, accounts, date ranges |
| `googleads/token_functions.py` | OAuth2 access token refresh |
| `utils/helpers.py` | BigQuery utilities |
| `utils/email.py` | Success/failure email notifications |

### 3. Automatic BigQuery loading
- Deletes the configured date window  
- Appends new records  
- Enforces schema defined in `settings.py`  
- Supports incremental and full-year refreshes 

## 🔐 BigQuery Service Account Setup

This pipeline can authenticate to BigQuery in two ways:

1. **Application Default Credentials (ADC)**  
   Used automatically when running in GCP (Cloud Run, Cloud Functions, VM with attached service account).

2. **Local service account JSON key**  
   Used when running locally or outside GCP.

If ADC is not available, the pipeline falls back to a JSON key based on the structure defined in `utils/helpers.py`:

```
secrets/<bq_project>/<bq_project>-bigquery.json
```

### How to create and place the BigQuery key

1. Go to **Google Cloud Console → IAM & Admin → Service Accounts**.
2. Create a new service account (or select an existing one).
3. Assign the following roles:
   - `BigQuery Data Viewer`
   - `BigQuery Job User`
   - `BigQuery Data Editor`
4. Generate a **JSON key** and download it.
5. In your project, create the folder:

```
secrets/<bq_project>/
```

Example for project `my-gcp-project`:

```
secrets/my-gcp-project/
```

6. Save the JSON key file inside this folder with the exact name:

```
my-gcp-project-bigquery.json
```

7. Your final structure must look like:

```
secrets/
└── my-gcp-project/
    └── my-gcp-project-bigquery.json
```

8. Ensure this file is **never committed**.  
   It should remain local only (protected by `.gitignore`).

Once this is in place, `bq_connect()` will automatically load the correct BigQuery credentials whether the code is running locally or in GCP.


### 4. 🔔 Email Notifications (Success / Failure)
After each run, the pipeline automatically sends a notification email, including:

- Brand executed  
- Date range  
- Rows uploaded  
- Execution status (success/failure)  
- Error trace (if any)  

Uses Gmail credentials from:
```
secrets/gmail_credentials.json
```

---

## 🔧 Installation

### Clone the repository
```bash
git clone https://github.com/yourusername/google-ads-bq-automation.git
cd google-ads-bq-automation
```

### Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Credentials Setup

### 1. Google Ads OAuth Credentials  
Copy the template:

```bash
cp secrets/googleads-credentials.example.json secrets/googleads-credentials.json
```

Fill in:

```json
{
    "CLIENT_ID": "your-client-id.apps.googleusercontent.com",
    "CLIENT_SECRET": "your-client-secret",
    "REFRESH_TOKEN": "your-refresh-token",
    "DEVELOPER_TOKEN": "your-developer-token"
}
```

### 2. Gmail Credentials (for notifications)

```bash
cp secrets/gmail_credentials.example.json secrets/gmail_credentials.json
```

```json
{
    "username": "your-email@example.com",
    "password": "your-app-password"
}
```

---

## ⚙️ Configuration (settings.py)

### 1. Date Range Logic

Last N days:
```python
USE_LAST_N_DAYS = True
LAST_N_DAYS = 10
```

Full-year:
```python
USE_LAST_N_DAYS = False
```

---

### 2. Brand & Account Configuration

```python
accounts_data = {
    "brand_alpha": [
        {
            "project_id": "my_project",
            "dataset": "brand_alpha_marketing",
            "table": "google_ads_daily",
            "accounts": [
                {
                    "account_id": "111-111-1111",
                    "acc_name": "brand alpha ae",
                    "customer_id": "1111111111"
                }
            ]
        }
    ]
}
```

---

## 🚀 Running the Pipeline

### Run:
```bash
python main.py
```

Pipeline flow:
1. Loads configs  
2. Refreshes OAuth token  
3. Fetches data for each account  
4. Merges and cleans data  
5. Deletes existing BigQuery rows  
6. Uploads new data  
7. Sends success/failure email  

---

## 🧩 Extending

- Add as many accounts as needed in `accounts_data`  
- Add/remove metrics in `table_schema`  
- Copy other platforms repositories to "platforms" folder, extend the list of tasks in main.py and have the multi-platform orchestration in place.

---

## 🔒 Security Notes

- Real secrets must **never** be committed  
- `.gitignore` already protects sensitive files  

---

## 🎉 Final Notes

This repository is a clean, production-ready template for multi-brand Google Ads → BigQuery automation, with structured collectors, secure credential handling, and run notifications.
