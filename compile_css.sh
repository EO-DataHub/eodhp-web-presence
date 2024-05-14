#!/bin/bash

for file in eodhp_web_presence/static/scss/*.scss; do
    [ -e "$file" ] || continue
    echo "Compiling $file";
    output_file="/css/$(basename "$file" .scss).css"
    output_file=eodhp_web_presence/static/"${output_file/scss/css}"
    python manage.py sass "$file" "$output_file";
done
