#!/usr/bin/bash
gunicorn -t 0 \
		 -w 16 \
		 -b 0.0.0.0:12031 \
		 all_in_one_server:app