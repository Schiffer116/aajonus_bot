.PHONY: build dev embed preprocess scrape scrape_imgs install run

install:
	@pip install -Ur requirements.txt

dev:
	@fastapi dev src.main:app

embed:
	@python3 scripts/embed.py

preprocess:
	@python3 scripts/preprocess.py

scrape:
	@python3 scripts/scrape.py

scrape_imgs:
	@python3 scripts/scrape_images.py

build: install scrape scrape_imgs preprocess embed
	cd ui && pnpm build

run: build
	@fastapi run src/main.py --host 0.0.0.0 --port 8001
