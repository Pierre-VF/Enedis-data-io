
.PHONY: install
install:
	uv sync
	echo "Install completed"

.PHONY: cleanup_code
cleanup_code:
	uv tool run isort --skip-gitignore --profile=black .
	(uv tool run pre-commit run --all) || (echo "Files were updated in precommits")
	# Running pre-commits a second time to ensure that issues that couldn't be fixed by the first run will block
	uv tool run pre-commit run --all
	echo "Code cleanup completed"
