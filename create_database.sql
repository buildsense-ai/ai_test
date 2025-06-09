-- AI评估平台数据库创建脚本
-- 请在腾讯云数据库中执行此脚本

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS ai_evaluation_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci
COMMENT 'AI对话代理评估平台数据库';

-- 2. 使用数据库
USE ai_evaluation_db;

-- 3. 显示创建成功消息
SELECT 'AI评估数据库创建成功！' AS message; 