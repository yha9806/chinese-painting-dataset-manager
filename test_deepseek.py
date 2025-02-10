import json
import os
from app.services.deepseek_service import analyze_painting_info, validate_painting_data, search_related_info

def ensure_test_data_dir():
    """确保测试数据目录存在"""
    os.makedirs("test_data", exist_ok=True)

def create_test_data():
    """创建测试数据文件"""
    test_data = {
        "title": "富春山居图",
        "artist": "黄公望",
        "dynasty": "元朝",
        "category": "山水画",
        "description": "中国十大传世名画之一",
        "size": "纵25.5厘米，横636.9厘米",
        "material": "纸本水墨",
        "collection": "浙江省博物馆",
        "creation_date": "约1350年"
    }
    
    ensure_test_data_dir()
    with open('test_data/test_painting.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)
    return test_data

def test_deepseek_services():
    try:
        # 确保测试数据存在
        if not os.path.exists('test_data/test_painting.json'):
            test_data = create_test_data()
        else:
            with open('test_data/test_painting.json', 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        
        print("原始数据：")
        print(json.dumps(test_data, ensure_ascii=False, indent=2))
        print("\n" + "="*50 + "\n")

        # 测试画作信息分析
        print("1. 测试画作信息分析：")
        enhanced_data = analyze_painting_info(test_data)
        print(json.dumps(enhanced_data, ensure_ascii=False, indent=2))
        print("\n" + "="*50 + "\n")

        # 测试数据验证
        print("2. 测试数据验证：")
        is_valid, message, validated_data = validate_painting_data(enhanced_data)
        print(f"验证结果：{is_valid}")
        print(f"验证信息：{message}")
        print("验证后数据：")
        print(json.dumps(validated_data, ensure_ascii=False, indent=2))
        print("\n" + "="*50 + "\n")

        # 测试相关信息搜索
        print("3. 测试相关信息搜索：")
        is_success, message, related_info = search_related_info(validated_data)
        print(f"搜索结果：{is_success}")
        print(f"搜索信息：{message}")
        print("相关信息：")
        for info in related_info:
            print(info)
            print("-" * 30)

    except Exception as e:
        print(f"测试过程中出错: {str(e)}")

if __name__ == "__main__":
    test_deepseek_services() 