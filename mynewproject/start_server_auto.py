#!/usr/bin/env python3
"""
Django Project Auto Startup Script (Non-interactive)
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description=None):
    """Run command and show progress"""
    if description:
        print(f"\n? {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"? {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"? Error: {e.stderr if e.stderr else str(e)}")
        return False


def check_django_installed():
    """Check if Django is installed"""
    try:
        import django
        print(f"? Django {django.VERSION[0]}.{django.VERSION[1]} is installed")
        return True
    except ImportError:
        print("? Django is not installed")
        return False


def install_requirements():
    """Install dependencies"""
    print("? Installing project dependencies...")
    return run_command("pip install -r requirements.txt", "Installing dependency packages")


def migrate_database():
    """Database migration"""
    print("?? Performing database migration...")
    
    # Create migration files
    if not run_command("python manage.py makemigrations", "Creating migration files"):
        return False
    
    # Execute migration
    return run_command("python manage.py migrate", "Executing database migration")


def create_superuser():
    """Create superuser automatically"""
    print("? Creating superuser automatically...")
    # Create superuser with username 'admin' and password 'admin123'
    os.environ['DJANGO_SUPERUSER_USERNAME'] = 'admin'
    os.environ['DJANGO_SUPERUSER_EMAIL'] = 'admin@example.com'
    os.environ['DJANGO_SUPERUSER_PASSWORD'] = 'admin123'
    
    return run_command("python manage.py createsuperuser --noinput", "Creating superuser")


def collect_static():
    """Collect static files"""
    if not os.path.exists('staticfiles'):
        print("? Collecting static files...")
        return run_command("python manage.py collectstatic --noinput", "Collecting static files")
    return True


def start_server():
    """Start development server"""
    print("\n? Starting Django development server...")
    print("? Access address: http://127.0.0.1:8000/")
    print("? Admin panel: http://127.0.0.1:8000/admin/")
    print("?? Image analysis: http://127.0.0.1:8000/")
    print("? Superuser credentials: admin/admin123")
    print("\nPress Ctrl+C to stop server\n")
    
    try:
        subprocess.run("python manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n\n? Server stopped")


def main():
    """Main function"""
    print("? Django AI Image Analyzer Auto Launcher")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('manage.py'):
        print("? Error: Please run this script in the project root directory")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("? Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"? Python {sys.version.split()[0]} detected")
    
    # Full initialization process (non-interactive)
    print("\n? Starting automatic initialization process...")
    
    if not check_django_installed():
        if not install_requirements():
            print("? Failed to install dependencies")
            sys.exit(1)
    
    if not migrate_database():
        print("? Database migration failed")
        sys.exit(1)
    
    create_superuser()
    
    print("\n? Initialization complete! Starting server...")
    start_server()


if __name__ == '__main__':
    main()