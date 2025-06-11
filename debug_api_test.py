#!/usr/bin/env python3
"""
Debug script to test the AI evaluation platform API directly
This helps identify if the issue is in the frontend or backend
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:3005"  # Change this to your deployed URL
TIMEOUT = 600  # 10 minutes timeout

# Sample API configuration for testing
SAMPLE_API_CONFIG = {
    "type": "custom-api",
    "url": "http://350f126b.r20.cpolar.top/v1/chat-messages",  # Update this with your working API URL
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-api-key"  # Update with your API key
    },
    "timeout": 30
}

# Sample requirement text
SAMPLE_REQUIREMENT_TEXT = """
智能建筑监理系统需求文档

1. 系统概述
本系统为建筑工程监理人员提供智能化工作支持，主要服务于现场监理工程师的日常工作需求。

2. 用户角色
- 现场监理工程师：负责施工现场质量控制和安全监督
- 专业经验：3-10年建筑工程监理经验
- 工作环境：建筑施工现场，需要快速准确的专业指导

3. 核心功能需求
- 规范标准查询：快速查找建筑施工规范和质量标准
- 质量检查指导：提供质量检查要点和验收标准
- 安全监督支持：安全隐患识别和处理建议
- 问题处理建议：常见质量问题的处理方案

4. 性能要求
- 响应速度：2秒内给出初步建议
- 准确性：基于现行国家和行业标准
- 实用性：适合现场快速决策使用
"""

async def test_health_endpoint():
    """测试健康检查端点"""
    print("🔍 Testing health endpoint...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

async def test_dynamic_evaluation():
    """Test the dynamic evaluation endpoint"""
    print("🚀 Testing dynamic evaluation endpoint...")
    print(f"⏰ Start time: {datetime.now()}")
    
    try:
        # Prepare form data
        form_data = {
            "agent_api_config": json.dumps(SAMPLE_API_CONFIG),
            "requirement_text": SAMPLE_REQUIREMENT_TEXT,
            "use_raw_messages": "false"
        }
        
        print("📤 Sending request to /api/evaluate-agent-dynamic...")
        print(f"📊 Form data size: {len(str(form_data))} characters")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            start_time = datetime.now()
            
            response = await client.post(
                f"{API_BASE_URL}/api/evaluate-agent-dynamic",
                data=form_data
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"⏱️ Request completed in {duration:.2f} seconds")
            print(f"📈 Response status: {response.status_code}")
            print(f"📏 Response size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("✅ Dynamic evaluation completed successfully!")
                    print(f"📊 Overall score: {result.get('evaluation_summary', {}).get('overall_score_100', 'N/A')}/100")
                    print(f"📋 Scenarios: {result.get('evaluation_summary', {}).get('total_scenarios', 'N/A')}")
                    print(f"💬 Conversations: {result.get('evaluation_summary', {}).get('total_conversations', 'N/A')}")
                    
                    # Check for response metadata
                    metadata = result.get('response_metadata', {})
                    if metadata:
                        print(f"📏 Response size: {metadata.get('size_mb', 'N/A')} MB")
                        print(f"⚡ Optimized: {metadata.get('optimized', False)}")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Response JSON decode error: {str(e)}")
                    print(f"📄 Raw response (first 1000 chars): {response.text[:1000]}")
                    return False
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"📄 Error response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print(f"⏰ Request timed out after {TIMEOUT} seconds")
        return False
    except httpx.ConnectError:
        print("❌ Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    print("🔧 AI Evaluation Platform API Debug Test")
    print("=" * 50)
    print(f"🌐 Target URL: {API_BASE_URL}")
    print(f"⏰ Timeout: {TIMEOUT} seconds")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = await test_health_endpoint()
    print()
    
    # Test 2: Dynamic evaluation (only if health check passes)
    if health_ok:
        eval_ok = await test_dynamic_evaluation()
        print()
        
        if eval_ok:
            print("🎉 All tests passed! The API is working correctly.")
        else:
            print("❌ Dynamic evaluation test failed.")
    else:
        print("❌ Skipping dynamic evaluation test due to health check failure.")
    
    print("\n🏁 Test completed.")

if __name__ == "__main__":
    asyncio.run(main()) 