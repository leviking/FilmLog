#!/bin/bash
# $1 = database
# $2 = user
# $3 = password

mysql $1 -u$2 -p$3 < database/schema.sql
mysql $1 -u$2 -p$3 < database/base-data.sql
