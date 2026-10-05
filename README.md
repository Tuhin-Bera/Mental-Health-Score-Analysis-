# Mental Health Signal

Mental Health Signal is a small web application for exploring how reported student lifestyle and social-media habits relate to a model-estimated mental-health score. A FastAPI service hosts both the browser interface and the prediction API.

> **Important:** This is an educational project, not a medical or mental-health assessment. It does not provide a diagnosis, treatment advice, or a substitute for support from a qualified professional. Do not use it to make decisions about an individual's care.

## Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Run Locally](#run-locally)
- [Application Workflow](#application-workflow)
- [API Reference](#api-reference)
- [Validation and Smoke Checks](#validation-and-smoke-checks)
- [Deploy to Render](#deploy-to-render)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Privacy and Model Notes](#privacy-and-model-notes)

## Features

- Browser form for entering a student profile and daily habits.
- Server-side request validation and a prediction from the saved scikit-learn model.
- A result view that presents the returned score with explanatory context.
- FastAPI interactive API documentation at `/docs` and an operational health endpoint at `/health`.

## Project Structure

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI application, input schema, health route, and prediction route. |
| `index.html` | Browser interface markup. |
| `script.js` | Form behavior, client-side validation, and API requests. |
| `style.css` | Interface styling. |
| `Mental_Health_Model.pkl` | Serialized model loaded by the application at startup. |
| `Student Social Media And Mental Health Impact.csv` | Project dataset. |
| `Mental_ML_project.ipynb` | Jupyter notebook for project analysis and model work. |
| `pyproject.toml` | Python project metadata and runtime dependencies. |
| `uv.lock` | Locked Python dependency resolution for uv. |

The model is loaded from the project root when `main.py` is imported. Keep the model file available in local runs and include it in deployments.

## Requirements

- Python 3.11 (the version specified in `.python-version`).
- `Mental_Health_Model.pkl` in the project root.
- Internet access during initial dependency installation.

## Run Locally

From the project root, create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the project and its dependencies, then start the development server:

```bash
python -m pip install --upgrade pip
python -m pip install .
uvicorn main:app --reload
```

The service listens at <http://127.0.0.1:8000/>. Open that address for the application, or <http://127.0.0.1:8000/docs> to explore and call the API interactively. Stop the server with `Ctrl+C`.

### Using uv

The repository includes `uv.lock`. If dependency metadata has changed, refresh the lock before a frozen install:

```bash
uv lock
uv sync --frozen
uv run uvicorn main:app --reload
```

When adding or changing a dependency, update `pyproject.toml`, run `uv lock`, and commit both files together.

## Application Workflow

1. The browser collects the profile and daily-habit fields and performs basic client-side checks.
2. On submission, the browser sends a JSON request to `POST /predict` on the same service origin.
3. FastAPI validates the request against the `StudentData` schema. Invalid fields receive a `422` response.
4. The service maps the values into the model's expected feature columns and derives `Grouped_country`. Countries outside the recognized list are grouped as `Other` for that feature.
5. The model predicts a score. The API returns the value rounded to two decimal places, and the browser displays it.

## API Reference

### `GET /health`

Returns a simple process health response:

```json
{"status":"ok"}
```

### `POST /predict`

Send a JSON object with all fields below. Enum values are case-sensitive.

| Field | Type | Allowed values or range |
| --- | --- | --- |
| `age` | integer | 10 to 100, inclusive |
| `gender` | string | `Male`, `Female` |
| `country` | string | Country name or other non-empty text |
| `academic_level` | string | `Undergraduate`, `Graduate`, `High School` |
| `most_used_platform` | string | `Facebook`, `LinkedIn`, `Instagram`, `Snapchat`, `Twitter`, `YouTube`, `TikTok`, `LINE`, `KakaoTalk`, `VKontakte`, `WhatsApp`, `WeChat` |
| `purpose_of_use` | string | `Networking`, `Education`, `Entertainment`, `News` |
| `avg_daily_usage_hours` | number | 0 to 24, inclusive |
| `daily_unlocks` | integer | 0 or greater |
| `study_hours` | number | 0 to 24, inclusive |
| `physical_activity_hours` | number | 0 to 24, inclusive |
| `sleep_hours_per_night` | number | 0 to 24, inclusive |
| `stress_level` | string | `Low`, `Medium`, `High`, `Very High` |

Example request:

```json
{
  "age": 21,
  "gender": "Female",
  "country": "India",
  "academic_level": "Undergraduate",
  "most_used_platform": "Instagram",
  "purpose_of_use": "Entertainment",
  "avg_daily_usage_hours": 4.5,
  "daily_unlocks": 60,
  "study_hours": 5,
  "physical_activity_hours": 1,
  "sleep_hours_per_night": 7,
  "stress_level": "Medium"
}
```

Successful response:

```json
{"predicted_mental_health_score":7.25}
```

The numeric response above is illustrative; the actual value depends on the input and model. Requests with missing or invalid values return HTTP `422` with validation details.

## Validation and Smoke Checks

There is currently no automated test suite in the repository. After starting the service, use these checks to verify the main paths:

1. Visit `/` and confirm the form loads.
2. Visit `/health` and confirm the response is `{"status":"ok"}`.
3. Open `/docs`, submit a valid `POST /predict` example, and confirm the response contains a numeric `predicted_mental_health_score`.
4. Submit an invalid value, such as an age below 10, and confirm the API returns `422`.

## Deploy to Render

Deploy this as a **Web Service**, not as a static site: the frontend depends on the FastAPI prediction endpoint, and both are served by one process.

1. Push the project to a Git repository accessible to Render. Confirm `Mental_Health_Model.pkl` is committed.
2. In Render, create a new Web Service and select the repository.
3. Set the root directory to the repository root (or leave it blank if Render already uses the root).
4. Select the Python runtime and configure Python 3.11.
5. Set the build command to:

	```bash
	python -m pip install .
	```

6. Set the start command to:

	```bash
	uvicorn main:app --host 0.0.0.0 --port $PORT
	```

7. Optionally set the health check path to `/health`, then deploy.
8. After deployment, check the service URL, `/health`, and `/docs`, then submit a prediction through the site.

Render supplies the listening port through the `PORT` environment variable. Do not use the `part-1` project script as the Render start command: its helper binds to port `8000` instead of the assigned port. The `.python-version` file records `3.11`; set the same version in the Render service if it is not detected automatically.

## Development Workflow

1. Make application or interface changes in the relevant source file.
2. For dependency changes, edit `pyproject.toml` and refresh `uv.lock` with `uv lock`.
3. Run the service locally and perform the smoke checks above, including a valid and invalid prediction request.
4. Review the change and ensure the model artifact is still present before pushing or deploying.

No formatter, linter, or automated test command is currently configured in the repository.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Startup fails with a missing model file | Confirm `Mental_Health_Model.pkl` exists in the repository root and is included in the deployment. |
| Startup fails with an import or dependency error | Confirm the build command completed successfully and dependencies in `pyproject.toml` installed. |
| Render reports that the service did not bind to a port | Use the Render start command above so Uvicorn binds to `$PORT` on `0.0.0.0`. |
| Prediction returns `422` | Compare the request field names, required fields, ranges, and exact enum values with the API table. |
| Browser cannot reach the API | Open the deployed service URL directly, confirm deployment succeeded, and check `/health`. |
| uv reports that the lockfile needs updating | Run `uv lock`, then retry the uv install command. |

## Privacy and Model Notes

- The application code does not write prediction requests to a database. Hosting, proxy, or browser logs may have separate retention behavior; review the deployment provider's settings and policies.
- Avoid entering personally identifying or sensitive health information into a public deployment.
- A serialized Python model is executable input to `joblib.load`. Only deploy model files from a trusted source.
- Keep the scikit-learn version compatible with the version used to create the model. The declared dependency versions are in `pyproject.toml`.
- Model predictions can be inaccurate or biased and should not be interpreted as a clinical score or an individual's mental-health status.
