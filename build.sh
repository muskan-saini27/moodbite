
#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# TEMPORARY: Create or repair production admin account
python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("MOODBITE_ADMIN_USERNAME")
password = os.environ.get("MOODBITE_ADMIN_PASSWORD")
email = os.environ.get("MOODBITE_ADMIN_EMAIL", "")

if not username or not password:
    raise RuntimeError("Production admin credentials are missing!")

user, created = User.objects.get_or_create(
    username=username,
    defaults={"email": email}
)

user.email = email or user.email
user.is_active = True
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

print("Production admin account created or updated successfully.")
PY

python manage.py import_foods --file moodbite_master_final_v2_indian_pricing_5615.csv
