# ? AI图片分析器 - 运行指南

## ? 准备工作

### 1. 安装Python环境
确保已安装Python 3.8+：
```bash
python --version
```

### 2. 安装Django
```bash
pip install django
```

### 3. 安装项目依赖
```bash
cd mynewproject
pip install -r requirements.txt
```

## ? 快速启动

### 方法一：使用启动脚本（推荐）
```bash
python start_server.py
```

按照提示选择：
1. 完整初始化（推荐）
2. 启动服务器

### 方法二：手动步骤

1. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

2. **创建超级用户**（可选）
```bash
python manage.py createsuperuser
```

3. **启动开发服务器**
```bash
python manage.py runserver
```

## ? 访问应用

- **主应用**：http://127.0.0.1:8000/
- **管理后台**：http://127.0.0.1:8000/admin/

## ? 配置Kimi API

### 1. 获取Kimi API密钥
访问 [Kimi官网](https://kimi.moonshot.cn/) 获取API密钥

### 2. 配置API密钥
编辑 `mynewproject/settings.py`：
```python
KIMI_API_KEY = 'your-actual-kimi-api-key'
```

或者使用环境变量：
```bash
export KIMI_API_KEY="your-actual-kimi-api-key"
```

### 3. 配置API地址
根据Kimi API文档调整：
```python
KIMI_API_BASE_URL = 'https://api.kimi.com/v1'
```

## ? 项目结构说明

```
mynewproject/
├── manage.py                 # Django管理脚本
├── start_server.py          # 一键启动脚本
├── requirements.txt         # 项目依赖
├── mynewproject/           # 主项目配置
│   ├── settings.py        # 配置文件（包含Kimi API配置）
│   ├── urls.py             # 主URL路由
│   └── ...
├── imageprocessor/          # 图片处理器应用
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图函数
│   ├── forms.py            # 表单验证
│   ├── kimi_service.py     # Kimi API服务
│   └── ...
├── templates/               # HTML模板
│   └── imageprocessor/
│       ├── upload.html     # 上传页面
│       ├── result.html     # 结果页面
│       └── history.html    # 历史页面
└── media/                   # 上传的图片存储位置
```

## ? 功能说明

### 主要功能
- ? **图片上传**：支持拖拽和点击上传
- ? **AI分析**：调用Kimi API进行图片内容分析
- ? **结果展示**：美观的结果展示页面
- ? **历史记录**：查看所有处理过的图片
- ? **结果保存**：自动保存分析结果
- ? **分享功能**：支持复制结果和分享链接

### 支持的图片格式
- JPG/JPEG
- PNG
- GIF
- BMP
- WebP

### 文件限制
- 最大文件大小：10MB
- 支持批量处理：暂不支持（后续版本添加）

## ?? 常见问题

### 1. 端口被占用
```bash
# 使用其他端口
python manage.py runserver 8080
```

### 2. 数据库错误
```bash
# 删除数据库文件重新创建
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### 3. 静态文件问题
```bash
# 收集静态文件
python manage.py collectstatic
```

### 4. 图片上传失败
- 检查图片格式是否支持
- 检查文件大小是否超过10MB
- 检查媒体目录权限

### 5. Kimi API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查API配额是否用完
- 查看错误日志获取详细信息

## ? 安全建议

### 生产环境部署
1. **修改密钥**：
   ```python
   SECRET_KEY = 'your-very-secret-key'
   ```

2. **关闭调试模式**：
   ```python
   DEBUG = False
   ```

3. **配置允许的域名**：
   ```python
   ALLOWED_HOSTS = ['your-domain.com']
   ```

4. **使用HTTPS**

5. **配置防火墙**

### API密钥安全
- 使用环境变量存储API密钥
- 定期更换API密钥
- 监控API使用情况

## ? 技术支持

如果遇到问题：

1. 检查错误日志
2. 查看Django文档
3. 检查Kimi API文档
4. 在GitHub提交Issue

## ? 开始使用

现在你可以：

1. 打开浏览器访问 http://127.0.0.1:8000/
2. 上传一张图片试试
3. 查看AI分析结果
4. 浏览处理历史

祝你使用愉快！?