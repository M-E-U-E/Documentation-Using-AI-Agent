## Setup

### Create a Virtual Environment

#### On macOS/Linux:
```bash
python3 -m venv env
source env/bin/activate
```

#### On Windows:
```bash
python -m venv env
env\Scripts\activate
```

### Docker Setup

1. Build and run the Docker containers:
   ```bash
   docker compose up --build
   ```

2. Open another terminal and run the following commands:
   ```bash
   docker exec -it cron_Django python manage.py makemigrations
   docker exec -it cron_Django python manage.py migrate
   ```

### Create Superuser

To create a superuser, run:
```bash
docker exec -it cron_Django python manage.py createsuperuser
```

---

<!-- ## Setting up PostgreSQL

1. Go to [http://localhost:5050/](http://localhost:5050/).

2. Enter these credentials and press the Login button:
   - **Email Address / Username**: `admin@admin.com`
   - **Password**: `admin123`

3. Register a new server:
   - **Right-click** on `Servers` and then select `Register > Server`.

4. In the **General tab**, enter:
   - **Name**: `testCRON`

5. In the **Connection tab**, enter:
   - **Host name/address**: `cron_Postgres`
   - **Username**: `postUser`
   - **Password**: `password`

6. Click **Save**.

7. Navigate to:
   - `Servers > testCRON > Databases > cron_db > Schemas > public > Tables`

8. To view a table, click on **View/Edit Data > All Rows**. -->
