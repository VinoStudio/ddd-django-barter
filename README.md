## Running the Application

This project is containerized with Docker for easy setup and deployment. Follow these steps to get started:

### Requirements:

- Docker and Docker Compose are installed on your system
- Git (to clone the repository)

### Setup: 
1. Clone the repository:
```bash
git clone https://github.com/VinoStudio/ddd-django-barter.git
```

```bash
cd [repo-directory]
```

2. Configure environment variables

```bash
cp .env.example .env
```
Edit the .env file with your preferred settings

### Starting and Stopping the Application
The application uses a Docker Compose setup with multiple services:
1. Run the application:
- If this is the first time running, run the following command:
```bash
make app
```
- Then run the following command to apply django-migrations:
```bash
make migrations
```
- Next time, it's enough to run:
```bash
make app
```

2. Stop the application running containers by:
```bash
make down
```

3. Access to application logs by:
```bash
make logs
```

### Accessing Services

Once running, you can access:
- Auth Service API: http://localhost:8005/
- PgAdmin: http://localhost:5443

You can change project settings by editing the .env file
