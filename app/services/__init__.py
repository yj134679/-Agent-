"""
服务模块 - 提供 LLM 和图片生成服务
"""
from app.services.llm_service import llm_service, LLMUsageInfo, TopicsResponse, StreamResult
from app.services.image_service import image_service


def get_llm_service():
    """获取 LLM 服务实例"""
    return llm_service


def get_image_service():
    """获取图片服务实例"""
    return image_service
