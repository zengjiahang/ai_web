#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.kimi_service import KimiService
import requests

print("=== Testing Kimi API Connection ===")

# 测试API连接
service = KimiService()

# 测试API端点是否可达
try:
    print(f"Testing connection to: {service.base_url}")
    response = requests.get(service.base_url.replace('/chat/completions', ''), timeout=10)
    print(f"Connection test status: {response.status_code}")
except Exception as e:
    print(f"Connection test failed: {e}")

# 测试API密钥格式
print(f"API Key format check: {service.api_key[:10]}...")
if len(service.api_key) < 20:
    print("❌ API Key seems too short")
else:
    print("✅ API Key length looks reasonable")

print("\n=== Kimi API Documentation ===")
print("Kimi API (Moonshot) 的正确配置:")
print("- Base URL: https://api.moonshot.cn/v1")
print("- 支持图片分析的模型: moonshot-v1-vision-preview")
print("- 确保API密钥有图片分析权限")