<h1 align="center">Page analyzer</h1>

### Hexlet tests and linter status:
[![Actions Status](https://github.com/bloodywd/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/bloodywd/python-project-83/actions)
[![Github Actions Status](https://github.com/bloodywd/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/bloodywd/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/b18375dd1b1733fa986d/maintainability)](https://codeclimate.com/github/bloodywd/python-project-83/maintainability)


## About the project.

Page analyzer is a small web-interface application for SEO quality assurance tests similar to PageSpeed Insights. 
[See the example](https://page-analyzer-26u6.onrender.com/)

## How to start

```
make build
make start
```
To use the app you'll need to provide it with $DATABASE_URL and $SECRET_KEY vars.

## System requirements

- Python 3.10
- PostgreSQL 12.14
