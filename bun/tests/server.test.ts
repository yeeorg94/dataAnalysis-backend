import { describe, it, expect, beforeAll, afterAll } from 'bun:test';
import type { Server } from 'bun';

describe.skip('HTTP Server Tests', () => {
  let server: Server;
  let baseUrl: string;
  const testPort = 3001; // 使用不同的端口避免冲突

  beforeAll(async () => {
    // 导入必要的模块
    const { handleRequest } = await import('../src/controllers/analyze.controller.js');
    const { getConfig } = await import('../src/utils/config.js');
    const config = getConfig();
    
    // 创建测试服务器
    server = Bun.serve({
      port: testPort,
      hostname: 'localhost',
      fetch: handleRequest,
      error(error) {
        console.error('服务器错误:', error);
        return new Response('Internal Server Error', { status: 500 });
      }
    });
    
    // 等待服务器启动
    await new Promise(resolve => setTimeout(resolve, 200));
    
    baseUrl = `http://localhost:${testPort}`;
  });

  afterAll(() => {
    if (server) {
      server.stop();
    }
  });

  describe('健康检查接口', () => {
    it('GET / 应该返回服务信息', async () => {
      const response = await fetch(`${baseUrl}/`);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.status).toBe('健康');
      expect(data.timestamp).toBeDefined();
      expect(data.environment).toBeDefined();
    });

    it('GET /health 应该返回健康状态', async () => {
      const response = await fetch(`${baseUrl}/health`);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.status).toBe('健康');
    });
  });

  describe('CORS支持', () => {
    it('OPTIONS请求应该返回正确的CORS头', async () => {
      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'OPTIONS'
      });
      
      expect(response.status).toBe(200);
      expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
      expect(response.headers.get('Access-Control-Allow-Methods')).toContain('POST');
      expect(response.headers.get('Access-Control-Allow-Headers')).toContain('Content-Type');
    });
  });

  describe('通用解析接口', () => {
    it('POST /analyze 应该处理抖音链接', async () => {
      const testData = {
        url: '3.56 复制打开抖音，看看【央广军事的作品】# 他新创作的九三阅兵BGM再次刷屏 # 请祖国检... G@V.lp eoD:/ 02/08',
        type: 'png',
        format: 'json'
      };

      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });

      expect(response.status).toBe(200);
      expect(response.headers.get('Content-Type')).toContain('application/json');
      
      const data = await response.json();
      expect(data.code).toBeDefined();
      expect(data.message).toBeDefined();
      
      // 如果成功解析，应该有data字段
      if (data.code === 200) {
        expect(data.data).toBeDefined();
        expect(data.data.app_type).toBe('douyin');
      }
    });

    it('POST /analyze 应该处理小红书链接', async () => {
      const testData = {
        url: '76 追追米大王发布了一篇小红书笔记，快来看吧！ 😆 35ajO3NDvPp 😆 复制本条信息，打开【小红书】App查看精彩内容！',
        type: 'png',
        format: 'json'
      };

      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });

      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data.code).toBeDefined();
      expect(data.message).toBeDefined();
      
      // 如果成功解析，应该有data字段
      if (data.code === 200) {
        expect(data.data).toBeDefined();
        expect(data.data.app_type).toBe('xiaohongshu');
      }
    });

    it('POST /analyze 应该处理无效输入', async () => {
      const testData = {
        url: '这里没有任何链接',
        type: 'png',
        format: 'json'
      };

      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });

      const data = await response.json();
      expect(data.code).toBe(500);
      expect(data.data).toBeNull();
      expect(data.message).toContain('未找到有效的URL');
    });
  });

  describe('专用解析接口', () => {
    it('POST /analyze/douyin 应该处理抖音链接', async () => {
      const testData = {
        url: '6.69 复制打开抖音，看看【别捏七七的作品】道可道 非常道# 道德经 # 一口气挑战 zgO:/ f@O.Kw 04/18',
        type: 'png'
      };

      const response = await fetch(`${baseUrl}/analyze/douyin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });

      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data.code).toBeDefined();
      expect(data.message).toBeDefined();
    });

    it('POST /analyze/xiaohongshu 应该处理小红书链接', async () => {
      const testData = {
        url: '35 俊英陈发布了一篇小红书笔记，快来看吧！ 😆 7gbQpJof4jZ 😆 复制本条信息，打开【小红书】App查看精彩内容！',
        type: 'png'
      };

      const response = await fetch(`${baseUrl}/analyze/xiaohongshu`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });

      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data.code).toBeDefined();
      expect(data.message).toBeDefined();
    });
  });

  describe('错误处理', () => {
    it('不存在的路由应该返回404', async () => {
      const response = await fetch(`${baseUrl}/nonexistent`);
      const data = await response.json();
      
      expect(response.status).toBe(404);
      expect(data.code).toBe(404);
      expect(data.message).toBe('Not Found');
    });

    it('不支持的HTTP方法应该返回405', async () => {
      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'GET'
      });
      
      expect(response.status).toBe(405);
      
      const data = await response.json();
      expect(data.code).toBe(405);
      expect(data.message).toBe('Method Not Allowed');
    });

    it('无效的JSON应该返回错误', async () => {
      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: 'invalid json'
      });
      
      const data = await response.json();
      expect(data.code).toBe(500);
    });
  });
});