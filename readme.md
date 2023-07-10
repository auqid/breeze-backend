# Breeze Backend

This is a Django project for Breeze, a web application that provides various features.

## Setup

To set up the project locally, follow these steps:

1. Clone the repository by running the following command:

   ```shell
   git clone https://github.com/naveedkhan1998/breeze-backend.git
   ```

2. Change into the project directory:

   ```shell
   cd breeze-backend
   ```

3. Build and start the Docker containers using `docker-compose`:

   ```shell
   docker-compose up --build
   ```

   This command will build the necessary Docker images and start the containers.

4. Once the containers are successfully built and running, you can make a request to the following URL:

   [http://localhost:5000/core/setup/](http://localhost:5000/core/setup/)

   This URL is where you can perform the setup for the Breeze application.

## Notes

- Make sure you have Docker and Docker Compose installed on your system before running the project.
- If port 5000 is already in use on your machine, you can modify the `docker-compose.yml` file to use a different port for the Breeze application.
- For any issues or questions, please refer to the project's [issue tracker](https://github.com/naveedkhan1998/breeze-backend/issues) on GitHub.
