<!-- # Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files. -->
<body>
    <header>
        <h1>Django-CRON</h1>
    </header>
    <main>
        <h2>Introduction</h2>
        <p>Django-CRON is a project aimed at setting up and running cron jobs in a Django application using Docker. This repository provides the necessary scripts and instructions to get your Django cron jobs up and running.</p>
        <h2>Features</h2>
        <ul>
            <li>Easy setup of virtual environments for both macOS/Linux and Windows</li>
            <li>Docker integration for managing Django migrations and creating superusers</li>
            <li>Instructions for running cron jobs within the Django application</li>
        </ul>
        <h2>Prerequisites</h2>
        <ul>
            <li>Python 3.x</li>
            <li>Docker</li>
        </ul>
        <h2>Setup</h2>
        <h3>Create a Virtual Environment</h3>
        <h4>On macOS/Linux:</h4>
        <pre><code>python3 -m venv env
source env/bin/activate</code></pre>       
        <h4>On Windows:</h4>
        <pre><code>python -m venv env
env\Scripts\activate</code></pre>
        <h3>Docker Setup:</h3>
        <pre><code>
docker compose up --build
//open another terminal and then:
docker exec -it cron_Django python manage.py makemigrations
docker exec -it cron_Django python manage.py migrate</code></pre>
        <h3>Create Superuser:</h3>
        <pre><code>docker exec -it cron_Django python manage.py createsuperuser</code></pre>
       <h3>Setting up PostgreSQL</h3>
       <pre>Go to http://localhost:5050/
Enter these credentials and press the Login button:
Email Address / Username: admin@admin.com
Password: admin123
Right click on Servers and then Register > Server
In General tab, enter Name: testCRON
In Connection tab, enter these details and click Save
Host name/address: cron_Postgres
Username: postUser
Password: password
Then go to Servers > testCRON > Databases > cron_db > Schemas > public > Tables
To view table click on View/Edit Data > All Rows
</pre>
        <h2>Running Cron Jobs</h2>
        <p>To run cron jobs, go to the <code>manage.py</code> directory and run these commands:</p>
        <pre><code># Install dependencies
**run this from the root directory**
pip install -r requirements.txt
            
# Change the CSV file path:(Defaults are:)
file_path = "C:/Users/User/Downloads/KayakTransactionReport.csv"
output_file = "C:/Users/User/Downloads/ProcessedReport.csv"
            
# Run cron jobs
cd cron_project
python manage.py runcrons

# Open Django shell
python manage.py shell

# Import and run the cron job
from import_export.cron_jobs import FileProcessingCronJob

cron = FileProcessingCronJob()
cron.do()

# Exit the shell
exit()</code></pre>
    </main>
</body>