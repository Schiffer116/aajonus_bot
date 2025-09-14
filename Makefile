run:
	@python3 src/main.py

embed:
	@python3 scripts/embed.py

preprocess:
	@python3 scripts/preprocess.py

scrape:
	@python3 scripts/scrape.py

scrape_imgs:
	@python3 scripts/scrape_imagess.py

install:
	@pip install -Ur requirements.txt
