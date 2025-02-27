#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.exceptions import ImproperlyConfigured

from dotenv import load_dotenv

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def main():
    """Run administrative tasks."""

    if os.path.exists(DOTENV_PATH):
        load_dotenv(DOTENV_PATH)
    else:
        raise RuntimeError(
            "Missing .env file! Ensure the environment variables are set properly."
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UA_13XX_bravo.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
        ) from exc
    except ImproperlyConfigured as exc:
        print(f"Django settings error: {exc}")
        sys.exit(1)

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
