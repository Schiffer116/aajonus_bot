run:
	@python3 main.py

embed:
	@python3 scripts/embed.py

scrape:
	@python3 scripts/scrape.py

install:
	@pip install -Ur requirements.txt
