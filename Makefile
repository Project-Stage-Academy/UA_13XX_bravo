#Makefile
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up --build

run:
	python manage.py runserver

migrate:
	python manage.py migrate

#make pytest ARGS="notifications/tests"
#print only the first failure test !!!!!
pytest:
	clear
	pytest -x $(ARGS)