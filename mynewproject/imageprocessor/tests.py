from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ProcessedImage
import tempfile
from PIL import Image
import io


class ImageProcessorTests(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 创建一个测试图片
        self.test_image = self.create_test_image()
        
    def create_test_image(self):
        """创建测试图片"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.seek(0)
        return SimpleUploadedFile(
            'test.jpg',
            file.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_upload_page_status_code(self):
        """测试上传页面状态码"""
        response = self.client.get(reverse('imageprocessor:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI图片智能分析')
    
    def test_history_page_status_code(self):
        """测试历史页面状态码"""
        response = self.client.get(reverse('imageprocessor:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '处理历史')
    
    def test_image_upload_form(self):
        """测试图片上传表单"""
        # 测试GET请求
        response = self.client.get(reverse('imageprocessor:upload'))
        self.assertContains(response, '上传图片')
        
        # 测试POST请求（无文件）
        response = self.client.post(reverse('imageprocessor:upload'))
        self.assertEqual(response.status_code, 200)
    
    def test_processed_image_model(self):
        """测试ProcessedImage模型"""
        image = ProcessedImage.objects.create(
            image=self.test_image,
            result='测试分析结果',
            status='completed'
        )
        
        self.assertEqual(image.result, '测试分析结果')
        self.assertEqual(image.status, 'completed')
        self.assertTrue(image.uploaded_at)
        self.assertIsNotNone(str(image))