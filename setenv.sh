#!/bin/sh

alias down='docker compose down -v'
alias up='docker compose up'

alias raw='python3 src/store_raw_response.py'
alias etl='python3 src/main.py'
