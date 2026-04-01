import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import ProcessedImage, RAGImageFeature
from imageprocessor.image_matcher import ImageMatcher

# 获取RAG库中已审核的图片
approved_rags = RAGImageFeature.objects.filter(
    approval_status='approved'
).select_related('processed_image')

print(f'RAG库中已审核的图片数量: {approved_rags.count()}')

# 准备候选图片列表
candidate_images = []
for rag in approved_rags:
    img = rag.processed_image
    img_path = img.image.path
    print(f'候选图片: {img_path}')
    if os.path.exists(img_path):
        candidate_images.append((img_path, {
            'processed_image': img,
            'rag_feature': rag,
            'features': rag.feature_vector,
            'positions': {
                'slot': rag.slot_positions,
                'hole': rag.hole_positions,
                'chamfer': rag.chamfer_positions,
                'shoulder': rag.shoulder_positions,
                'step': rag.step_positions
            }
        }))
    else:
        print(f'  路径不存在!')

print(f'\\n候选图片数量: {len(candidate_images)}')

# 创建图像匹配器
image_matcher = ImageMatcher()

# 查找最相似的3张图片
query_image_path = 'd:/python/ai部署/图片/微信图片_20251123111536_70_19.jpg'
similar_images = image_matcher.find_similar_images_by_image(
    query_image_path, 
    candidate_images, 
    top_k=3
)

print(f'\\n找到 {len(similar_images)} 张相似图片')
for i, similar in enumerate(similar_images, 1):
    print(f'\\n相似图片 #{i}:')
    print(f'  路径: {similar["image_path"]}')
    print(f'  相似度: {similar["similarity"]:.2%}')
    print(f'  哈希距离: {similar["hash_distance"]}')
    print(f'  图片ID: {similar["metadata"]["processed_image"].id}')
    print(f'  特征: 槽{similar["metadata"]["features"]["slot"]} 孔{similar["metadata"]["features"]["hole"]} 倒角{similar["metadata"]["features"]["chamfer"]} 肩{similar["metadata"]["features"]["shoulder"]} 阶{similar["metadata"]["features"]["step"]}')