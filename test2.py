import os
import base64
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from openai import OpenAI
 
client = OpenAI(
    api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
    base_url="https://api.moonshot.cn/v1",
)
 
# 在这里，你需要将 kimi.png 文件替换为你想让 Kimi 识别的图片的地址
image_path = r"C:\Users\无敌暴龙战士\Desktop\python\ai部署\微信图片_20260304151829_116_19.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()
 
# 我们使用标准库 base64.b64encode 函数将图片编码成 base64 格式的 image_url
image_url = f"data:image/{os.path.splitext(image_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"
 
 
completion = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[
        {"role": "system", "content": "你是 Kimi。"},
        {
            "role": "user",
            # 注意这里，content 由原来的 str 类型变更为一个 list，这个 list 中包含多个部分的内容，图片（image_url）是一个部分（part），
            # 文字（text）是一个部分（part）
            "content": [
                {
                    "type": "image_url", # <-- 使用 image_url 类型来上传图片，内容为使用 base64 编码过的图片内容
                    "image_url": {
                        "url": image_url,
                    },
                },
                {
                    "type": "text",
                    "text": "请帮我分析图片里有几个槽特征，几个倒角特征，几个孔特征，几个阶特征，几个肩特征。", # <-- 使用 text 类型来提供文字指令，例如“描述图片内容”
                },
            ],
        },
    ],
)
 
print(completion.choices[0].message.content)
 