#! /bin/bash
gunicorn --name work_management --timeout "120" --log-level debug -b 0.0.0.0:1667 -w 8 wsgi:app

