#!/bin/bash
git pull && ./migrate.sh && sudo apachectl graceful
