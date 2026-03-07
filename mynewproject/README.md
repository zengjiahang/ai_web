# AI Image Analyzer

A Django-based web application that uses AI to analyze and describe images.

## Features

- 🖼️ **Image Upload**: Support for drag-and-drop and click-to-upload
- 🤖 **AI Analysis**: Integration with Kimi API for intelligent image analysis
- 📱 **Responsive Design**: Bootstrap 5 interface, mobile-friendly
- 📊 **Processing History**: View all processing records
- 💾 **Result Saving**: Automatic saving of analysis results
- 📤 **Sharing**: Support for copying results and sharing links

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Configure Kimi API

Edit `mynewproject/settings.py` and replace the API key:

```python
KIMI_API_KEY = 'your-actual-kimi-api-key'  # Replace with your Kimi API key
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the application.

### Alternative: Use Startup Script

```bash
python start_server.py
```

This script provides an interactive menu for easy setup and startup.

## Project Structure

```
mynewproject/
├── manage.py                 # Django management script
├── start_server.py          # Interactive startup script
├── requirements.txt         # Project dependencies
├── imageprocessor/          # Image processor app
│   ├── models.py           # Data models
│   ├── views.py            # View functions
│   ├── forms.py            # Form validation
│   ├── kimi_service.py     # Kimi API service
│   └── ...
├── templates/               # HTML templates
│   └── imageprocessor/
│       ├── upload.html     # Upload page
│       ├── result.html     # Result page
│       └── history.html    # History page
└── media/                   # Uploaded images
```

## Usage

1. **Upload Image**: Click or drag image to upload area
2. **AI Analysis**: System automatically analyzes image content
3. **View Results**: See detailed AI-generated descriptions
4. **Browse History**: View all processed images

## Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- WebP

## Configuration

### File Upload Limits

- Maximum file size: 10MB
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`

### API Configuration

The application uses Kimi API for image analysis. Make sure to:

1. Obtain a valid API key from Kimi
2. Configure the API key in `settings.py`
3. Ensure proper API endpoint configuration

## Development

### Running Tests

```bash
python manage.py test
```

### Admin Panel

Access the admin panel at http://127.0.0.1:8000/admin/

## License

This project is open source and available under the MIT License.