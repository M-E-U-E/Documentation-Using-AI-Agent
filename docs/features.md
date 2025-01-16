# Features

The `cron_project` is equipped with a wide range of features designed to handle both manual and automated data workflows. Below is a detailed breakdown of its capabilities:

## 1. CSV Import and Export

- **Import CSV:** Administrators can upload transaction data using a simple CSV import interface. The system validates the uploaded data for errors, ensuring only accurate records are added.
- **Export CSV:** Selected transactions can be exported to CSV format, making it easy to share or analyze data externally.

## 2. Interactive Data Visualizations

- **Line Chart – Monthly Revenue vs. Commission:**  
  Displays monthly trends in revenue and commission to help administrators identify growth patterns and seasonal changes.
- **Pie Chart – Revenue by Country:**  
  Illustrates the geographic distribution of revenue, highlighting key markets and enabling strategic planning.

## 3. Stand-alone CRON Process

- **Automated Daily Execution:**  
  A CRON job runs every day at 1 PM to fetch a CSV file from the `static/data/` directory, process it, and generate a new file in the same location.
- **File-Based Data Processing:**  
  The CRON process operates independently of the PostgreSQL database, handling data transformations or updates directly within the file system.
- **Seamless Integration:**  
  While the CRON process is separate, its output complements the manual workflows by ensuring that files in `static/data/` remain updated.

### Workflow Diagram

The following diagram provides a visual overview of the project's key functionalities and workflow:

![Workflow Diagram](assets/img/fullFlow2.svg)


This diagram illustrates how various components—such as data import, validation, visualization, and export—integrate into the overall system.

## 4. Custom Admin Dashboard

- **Integrated Features:** All functionalities, including data import/export and visualizations, are embedded within the Django Admin interface for ease of use.
- **User-Friendly Design:** The admin interface maintains Django’s familiar look and feel while enhancing usability with additional tools.

## 5. Data Integrity and Maintenance

- **Unique Transaction IDs:** Ensures that all transactions are uniquely identified, preventing duplication and maintaining clean records.
- **Upsert Operations:** Automatically handles both the creation of new records and updates to existing records, ensuring data consistency.

## 6. Error Handling and Notifications

- **Validation Feedback:** Provides detailed error messages for invalid CSV uploads, allowing administrators to address issues promptly.
- **Notifications:** Uses Django’s messaging framework to inform users of the success or failure of data operations, ensuring transparency.

---