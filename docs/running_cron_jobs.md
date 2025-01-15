## Running Cron Jobs

To run cron jobs, follow these steps:

1. **Install Dependencies**

    Run the following command from the root directory:
    ```
    pip install -r requirements.txt
    ```

2. **Change the CSV File Paths**

    Update the file paths in your script :
    ```
    file_path = "...csv"
    output_file = "...csv"
    ```

3. **Run Cron Jobs**

    Navigate to the project directory and execute the cron jobs:

    ```
    cd cron_project
    python manage.py runcrons
    ```

4. **Open Django Shell**

    Start the python shell:

    ```
    python manage.py shell
    ```

5. **Import and Run the Cron Job**
   Execute the following commands in the Django shell:

        from import_export.cron_jobs import FileProcessingCronJob

        cron = FileProcessingCronJob()
        
        cron.do()

   

6. **Exit the Shell**

    Type `exit()` to leave the shell.
