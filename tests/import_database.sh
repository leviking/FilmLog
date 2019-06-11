#!/bin/bash
# $1 = database
# $2 = host
# $3 = user
# $4 = password

mysql $1 -h$2 -u$3 -p$4 < database/schema.sql
mysql $1 -h$2 -u$3 -p$4 < database/base-data.sql
