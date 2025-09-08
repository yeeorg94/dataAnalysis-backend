import type { AppConfig } from '../types/index.js';

// 环境类型枚举
export enum EnvType {
  DEV = 'development',
  PROD = 'production',
  TEST = 'testing'
}

// 获取当前环境
export function getEnvironment(): string {
  return process.env.APP_ENV || EnvType.DEV;
}

// 基础配置
class BaseConfig implements AppConfig {
  // 服务器设置
  host = '127.0.0.1';
  port = 3001;
  environment = getEnvironment() as 'development' | 'production' | 'testing';
  
  // 日志配置
  logLevel: 'debug' | 'info' | 'warn' | 'error' = 'info';
  
  // 请求头设置
  userAgents = {
    default: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    mobile: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/134.0.0.0'
  };
  
  // 关键词映射
  appTypeKeywords = {
    xiaohongshu: ['小红书', 'xhs', 'xiaohongshu'],
    douyin: ['抖音', 'douyin', 'dy']
  };
}

// 开发环境配置
class DevelopmentConfig extends BaseConfig {
  host = '127.0.0.1';
  port = 3002;
  logLevel: 'debug' | 'info' | 'warn' | 'error' = 'debug';
}

// 生产环境配置
class ProductionConfig extends BaseConfig {
  host = '0.0.0.0';
  port = parseInt(process.env.PORT || '3000');
  logLevel: 'debug' | 'info' | 'warn' | 'error' = 'info';
}

// 测试环境配置
class TestingConfig extends BaseConfig {
  host = '127.0.0.1';
  port = 3001;
  logLevel: 'debug' | 'info' | 'warn' | 'error' = 'debug';
}

// 配置映射
const configByEnv = {
  [EnvType.DEV]: DevelopmentConfig,
  [EnvType.PROD]: ProductionConfig,
  [EnvType.TEST]: TestingConfig
};

// 获取当前环境的配置
export function getConfig(): AppConfig {
  const env = getEnvironment() as EnvType;
  const ConfigClass = configByEnv[env] || DevelopmentConfig;
  return new ConfigClass();
}

// 当前配置实例
export const config = getConfig();