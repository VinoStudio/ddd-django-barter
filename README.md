## Running the Application

This project is containerized with Docker for easy setup and deployment. Follow these steps to get started:

### Requirements:

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

### Setup: 
1. Clone the repository:
```bach
git clone https://github.com/VinoStudio/ddd-django-barter.git
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
- if this is the first time running, run the following command:
```bash
make app
```
- then run the following command to apply django-migrations:
```bash
make mimigrations
```
- next time is enough to run:
```bash
make app
```

2.Stop application running containers by:
```bash
make down
```

### Accessing Services

Once running, you can access:
- Auth Service API: http://localhost:8005/
- PgAdmin: http://localhost:5443

You can change API port by editing the .env file
To change PgAdmin, Postgres ports, edit the docker-compose.yaml