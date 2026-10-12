
#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py import_foods --file moodbite_master_final_v2_indian_pricing_5615.csv
