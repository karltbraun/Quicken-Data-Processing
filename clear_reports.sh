#! /usr/bin/env bash

read -p "This will delete all CSV and PNG files in ./reports and ./reports/charts. Proceed? (y/n): " confirm
if [[ "$confirm" != [yY] ]]; then
    echo "Aborted."
    exit 1
fi
rm ./reports/*.csv
rm  ./reports/charts/*.png
