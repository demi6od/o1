#!/usr/bin/bash
gunicorn -t 0 \
		 -w 16 \
		 -b 0.0.0.0:12023 \
		 python_interpreter_server:app