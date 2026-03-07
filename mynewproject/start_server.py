#!/usr/bin/env python3
"""
Django Project Startup Script
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
    """Create superuser"""
    response = input("\n? Do you want to create a superuser? (y/n): ").strip().lower()
    if response == 'y':
        return run_command("python manage.py createsuperuser", "Creating superuser")
    return True


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
    print("\nPress Ctrl+C to stop server\n")
    
    try:
        subprocess.run("python manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n\n? Server stopped")


def main():
    """Main function"""
    print("? Django AI Image Analyzer Launcher")
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
    
    # Main menu
    while True:
        print("\n? Available operations:")
        print("1. Full initialization (recommended)")
        print("2. Install dependencies only")
        print("3. Database migration only")
        print("4. Create superuser only")
        print("5. Start server directly")
        print("6. Exit")
        
        choice = input("\nPlease select operation (1-6): ").strip()
        
        if choice == '1':
            # Full initialization process
            print("\n? Starting full initialization process...")
            
            if not check_django_installed():
                if not install_requirements():
                    continue
            
            if migrate_database():
                create_superuser()
                print("\n? Initialization complete! You can now start the server.")
                response = input("Start server immediately? (y/n): ").strip().lower()
                if response == 'y':
                    start_server()
            else:
                print("\n? Initialization failed, please check error messages")
            
        elif choice == '2':
            install_requirements()
            
        elif choice == '3':
            migrate_database()
            
        elif choice == '4':
            create_superuser()
            
        elif choice == '5':
            start_server()
            
        elif choice == '6':
            print("? Goodbye!")
            break
            
        else:
            print("? Invalid choice, please try again")


if __name__ == '__main__':
    main()