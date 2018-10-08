#! /bin/bash
gunicorn --name work_management --timeout "120" --log-level debug -t 3000 -b 0.0.0.0:1667 -w 4 wsgi:app

