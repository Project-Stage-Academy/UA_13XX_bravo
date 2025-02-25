#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.exceptions import ImproperlyConfigured


def main():
    """Run administrative tasks."""
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
