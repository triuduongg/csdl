#!/usr/bin/env python
import os
import sys
import socket

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'document_management.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Print local IP address and set default runserver address if not provided
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        print(f"Server running at http://{ip}:8000")
        if len(sys.argv) == 2:
            sys.argv.append('0.0.0.0:8000')

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
