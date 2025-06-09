#!/usr/bin/env python3
# 自动化数据库设置脚本

import pymysql
import sys

def create_database():
    """创建数据库"""
    print("🚀 开始设置AI评估平台数据库...")
    
    # 连接数据库服务器(不指定具体数据库)
    try:
        conn = pymysql.connect(
            host='gz-cdb-e0aa423v.sql.tencentcdb.com',
            port=20236,
            user='root',
            password='Aa@114514',
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✅ 数据库服务器连接成功")
        
        cursor = conn.cursor()
        
        # 创建数据库
        print("📝 创建数据库 ai_evaluation_db...")
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS ai_evaluation_db
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            COMMENT 'AI对话代理评估平台数据库'
        """)
        print("✅ 数据库创建成功")
        
        # 切换到新数据库
        cursor.execute("USE ai_evaluation_db")
        
        # 读取并执行表结构SQL
        print("📋 创建数据表结构...")
        try:
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # 分割SQL语句并执行
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for stmt in statements:
                if stmt.upper().startswith(('CREATE', 'INSERT', 'ALTER')):
                    try:
                        cursor.execute(stmt)
                        print(f"✅ 执行SQL: {stmt[:50]}...")
                    except Exception as e:
                        print(f"⚠️  SQL执行警告: {stmt[:50]}... - {e}")
            
            print("✅ 数据表结构创建完成")
            
        except FileNotFoundError:
            print("⚠️  database_schema.sql 文件未找到，请手动执行表结构创建")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 数据库设置完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

def test_final_connection():
    """测试最终连接"""
    print("\n🔍 测试最终数据库连接...")
    try:
        conn = pymysql.connect(
            host='gz-cdb-e0aa423v.sql.tencentcdb.com',
            port=20236,
            user='root',
            password='Aa@114514',
            database='ai_evaluation_db',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"✅ 连接成功！数据库包含 {len(tables)} 个表:")
        for table in tables:
            print(f"   📊 {table[0]}")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 最终连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI评估平台数据库自动设置")
    print("=" * 60)
    
    # 创建数据库和表
    if create_database():
        # 测试连接
        if test_final_connection():
            print("\n🎉 所有设置完成！现在可以启动AI评估平台了")
            print("   运行命令: python main.py")
        else:
            print("\n⚠️  数据库创建成功，但连接测试失败")
            sys.exit(1)
    else:
        print("\n❌ 数据库设置失败")
        sys.exit(1) 