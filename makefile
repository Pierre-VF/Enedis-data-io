
.PHONY: install
install:
	uv sync
	echo "Install completed"

.PHONY: cleanup_code
cleanup_code:
	uv tool run isort --skip-gitignore --profile=black .
	# uv tool run autoflake --in-place --remove-all-unused-imports --expand-star-imports --remove-duplicate-keys --remove-unused-variables --exclude=".*/__init__.py" -r .
	(uv tool run pre-commit run --all) || (echo "Files were updated in precommits")
	# Running pre-commits a second time to ensure that issues that couldn't be fixed by the first run will block
	uv tool run pre-commit run --all
	echo "Code cleanup completed"
