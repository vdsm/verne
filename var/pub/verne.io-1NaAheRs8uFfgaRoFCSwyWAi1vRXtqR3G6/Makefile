export PYTHONPATH ?= ../../lib/python/ 

generate:
	@pelican --debug

serve:
	uwsgi --http :9090 --wsgi-file usr/website/app.py --check-static usr/website/output --static-index index.html
