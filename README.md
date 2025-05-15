# Technical Support & Data Analysis Code Examples

Welcome to this repository of Python and SQL code examples, designed to demonstrate practical approaches to technical support automation, troubleshooting, and data analysis. These examples have been consolidated into an interactive Jupyter Notebook for ease of use, understanding, and execution.

## ✨ Main Feature: Interactive Jupyter Notebook

The primary way to explore and utilise these examples is through the **`Gong_Technical_Examples.ipynb`** Jupyter Notebook located in this repository.

This notebook provides:
* **Interactive Execution:** Run Python and SQL (adapted for SQLite) code cells directly within the notebook.
* **Detailed Explanations:** Each code section is accompanied by markdown cells explaining its purpose, logic, and how to interpret the results.
* **Self-Contained Environment:**
    * Python examples use dynamically generated sample data or temporary SQLite databases, which are created and cleaned up within the notebook.
    * SQL examples run against an in-memory SQLite database, requiring no external database setup.
* **Enhanced Visualisations:** The Log File Analyser features interactive charts created with Plotly.
* **British English:** All explanations and comments are provided in British English.

### Notebook Contents:

The `Gong_Technical_Examples.ipynb` notebook covers:

1.  **Setup:** Instructions and code to import necessary Python libraries.
2.  **Python Examples:**
    * **Log File Analyser:** Parses log files, identifies error patterns, analyses hourly distributions and error bursts, and generates interactive Plotly visualisations.
    * **API Response Analyser:** Analyses API call logs from a temporary SQLite database to identify failing requests, slow endpoints, and performance trends.
3.  **SQL Examples (Adapted for SQLite):**
    * **Database Setup:** Creates an in-memory SQLite database with schemas and sample data for the SQL queries.
    * **API Performance Analysis:** Identifies slow-performing API calls.
    * **Declining Usage Detection:** Pinpoints users with significantly decreasing engagement.
    * **Integration Sync Failures:** Identifies records failing to synchronise between systems.

## 🚀 How to Use the Notebook

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Open the Notebook:**
    You can open `Gong_Technical_Examples.ipynb` using:
    * Jupyter Notebook or JupyterLab.
    * Google Colaboratory (Colab) by uploading the `.ipynb` file.
    * Visual Studio Code (with Python and Jupyter extensions).

3.  **Install Dependencies:**
    The notebook uses several Python libraries. If you don't have them installed, you might need to run the following (the first code cell in the notebook also contains commented-out pip install commands):
    ```bash
    pip install pandas matplotlib plotly openpyxl nbformat
    ```
    *(Note: `openpyxl` and `nbformat` might be required by pandas or plotly for certain operations).*

4.  **Run Cells Sequentially:**
    Execute the cells in the notebook from top to bottom to see the explanations, code, and results.

## 📁 Original Scripts

This repository also contains the original standalone Python (`.py`) and SQL (`.sql`) scripts that were the basis for the examples in the Jupyter Notebook. These are located in their respective directories.

* **Python Scripts:**
    * `log_analyzer.py`
    * `api_response_analyzer.py`
* **SQL Scripts (Originally for PostgreSQL):**
    * `api_performance_analysis.sql`
    * `declining_usage_detection.sql`
    * `integration_sync_failures.sql`

**Note:** While these original scripts are available, they may require different setups (e.g., a running PostgreSQL instance for the SQL files, or specific file paths for the Python scripts). **For the most straightforward experience, using the `Gong_Technical_Examples.ipynb` notebook is highly recommended.**

## 🎯 Purpose and Use Cases

These examples are intended to:
* Demonstrate systematic troubleshooting methodologies.
* Provide a foundation for building more complex technical support automation tools.
* Serve as educational material for understanding data analysis techniques in a support context.
* Offer practical solutions for common challenges faced in enterprise SaaS support.

## 📜 Licence

Please refer to the LICENCE file in this repository for information on usage rights and limitations. (Assuming you might add one - if not, this line can be removed).

---

We hope you find these examples useful!
