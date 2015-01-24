export PYTHONPATH ?= lib/python

generate:
	pelican -o www -s settings.py content

serve:
	uwsgi --http :9090 --wsgi-file app.py --check-static www --static-index index.html --honour-stdin --py-autoreload 1
