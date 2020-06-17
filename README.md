## How to run locally

- Install docker and docker-compose
- Run `docker-compose build` to build your docker environment.
- Run `docker-compose up` to run locally.
- Access `http://localhost:8000/swagger/` to view the backend documentation using swagger.
- To create admin user, run `docker-compose run web python manage.py createsuperuser` then follow the instructions.