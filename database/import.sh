#!/bin/bash
DB="FilmLogDev"
mysql -Bse "DROP DATABASE $DB"
mysql -Bse "CREATE DATABASE $DB"
echo "Schema"
mysql $DB < schema.sql
echo "Base Data"
mysql $DB < base-data.sql
echo "Users"
mysql $DB < users-dev.sql

