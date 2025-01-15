# Project Directory Structure Overview

```
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── KayakTransactionReport.csv
├── README.md
├── requirements.txt
└── cron_project/
    ├── manage.py
    └── cron_project/
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
    └── import_export/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── cron_jobs.py
        ├── tests.py
        ├── utils.py
        ├── views.py
        └── migrations/
            ├── __init__.py
            ├── 0001_initial.py
            ├──0002_transaction_boom_score_delta_bucket_and_more.py
            ├──0003_kayaktransaction_transactionmetadata_and_more.py
            └── 0004_delete_transactionmetadata.py
    └── templates/
        └── admin/
            ├── change_list.html
            ├── import_csv_form.html
            └── custom_login.html
    └── static/
        └── admin/
            ├── css/
            │   └── custom_login.css
            └── img/
                └── admin_logo-rmbg.png

```