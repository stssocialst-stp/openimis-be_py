#!/usr/bin/env python
"""
Run Django migrations by calling manage.py migrate with SCHEDULER_AUTOSTART=False
This script just ensures the environment variable is set before Django initializes
"""
import os
import sys
import subprocess

# Set environment to prevent scheduler from starting
os.environ['SCHEDULER_AUTOSTART'] = 'False'
os.environ['NO_DATABASE'] = 'False'  # We DO want database access

print("=" * 60)
print("Running migrations with SCHEDULER_AUTOSTART=False...")
print("=" * 60)

# Change to Django directory
os.chdir('/openimis-be/openIMIS')

# Run migrate command
result = subprocess.run(
    [sys.executable, 'manage.py', 'migrate', '--noinput'],
    env=os.environ.copy(),
    capture_output=False
)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ Migrations completed successfully!")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print(f"❌ Migration failed with code {result.returncode}")
    print("=" * 60)

sys.exit(result.returncode)
