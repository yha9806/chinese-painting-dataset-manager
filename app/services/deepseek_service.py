from openai import OpenAI
from ..core.config import get_settings
import json

settings = get_settings()

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)

# 定义模型常量
DEEPSEEK_CHAT_MODEL = "deepseek-chat"  # DeepSeek-V3
DEEPSEEK_CODER_MODEL = "deepseek-reasoner"  # DeepSeek-R1

def analyze_painting_info(json_data: dict) -> dict:
    """分析画作信息并补充缺失数据"""
    try:
        # 构建提示信息
        prompt = f"作为中国画专家，请分析并补充以下画作信息：{json.dumps(json_data, ensure_ascii=False)}。\n请从画作基本信息、艺术特征、文化价值、创作背景和保存状况等方面进行分析。\n返回JSON格式的分析结果。"

        print(f"使用模型: {DEEPSEEK_CHAT_MODEL}")
        
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model=DEEPSEEK_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的中国画艺术研究专家。请以JSON格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        print("API响应内容:", response.choices[0].message.content)
        
        # 解析返回的JSON数据
        enhanced_data = json.loads(response.choices[0].message.content)
        json_data.update(enhanced_data)
        
        return json_data
    except Exception as e:
        print(f"错误详情: {str(e)}")
        return json_data

def validate_painting_data(json_data: dict) -> tuple[bool, str, dict]:
    """验证画作数据的完整性和准确性"""
    try:
        prompt = f"""作为中国画鉴定专家，请验证以下画作信息：{json.dumps(json_data, ensure_ascii=False)}
        请从时代考证、艺术特征、史料核对和完整性等方面进行验证。
        请以JSON格式返回，包含以下字段：
        {{
            "is_valid": true/false,
            "validation_details": {{
                "time_period_verification": "时代考证结果",
                "artistic_features_verification": "艺术特征验证",
                "historical_records_verification": "史料核对结果",
                "completeness_check": "完整性检查结果"
            }},
            "corrected_data": {{}},
            "reference_urls": []
        }}"""

        print(f"使用模型: {DEEPSEEK_CHAT_MODEL}")
        
        response = client.chat.completions.create(
            model=DEEPSEEK_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的中国画艺术鉴定专家。请以JSON格式返回验证结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        print("API响应内容:", response.choices[0].message.content)
        
        # 解析响应内容
        result = json.loads(response.choices[0].message.content)
        return result["is_valid"], json.dumps(result["validation_details"], ensure_ascii=False), result["corrected_data"]
    except Exception as e:
        print(f"错误详情: {str(e)}")
        return False, f"验证过程出错: {str(e)}", json_data

def search_related_info(json_data: dict) -> tuple[bool, str, dict]:
    """搜索画作相关信息"""
    try:
        # 艺术分析部分 - 使用V3模型
        art_prompt = f"""作为中国画艺术专家，请分析以下画作的艺术特征和历史背景：{json.dumps(json_data, ensure_ascii=False)}
请提供以下方面的分析：
1. 艺术特征和风格分析
2. 作品历史背景
3. 艺术家生平简介

请以结构化的方式返回分析结果。"""

        print(f"使用模型(艺术分析): {DEEPSEEK_CHAT_MODEL}")
        art_response = client.chat.completions.create(
            model=DEEPSEEK_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的中国画艺术研究专家。请提供详细的艺术分析。"},
                {"role": "user", "content": art_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        # 学术研究部分 - 使用R1模型
        research_prompt = f"""作为中国画学术研究专家，请提供以下画作的相关学术研究信息：{json.dumps(json_data, ensure_ascii=False)}
请从以下方面进行分析：
1. 相关学术研究成果
2. 重要文献记载
3. 艺术史地位评估
4. 参考来源

请提供详细的分析结果。"""

        print(f"使用模型(学术研究): {DEEPSEEK_CODER_MODEL}")
        research_response = client.chat.completions.create(
            model=DEEPSEEK_CODER_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的中国画学术研究专家。请提供详细的学术分析。"},
                {"role": "user", "content": research_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # 合并结果
        art_result = json.loads(art_response.choices[0].message.content)
        research_result = {
            "academic_research": research_response.choices[0].message.content
        }

        combined_result = {
            "artistic_analysis": art_result,
            "academic_research": research_result
        }

        return True, "信息检索成功", combined_result
    except Exception as e:
        print(f"错误详情: {str(e)}")
        return False, f"信息检索失败: {str(e)}", {} 