import type { AnalyzeRequest, ApiResponse, MediaData, HealthResponse } from '../types/index.js';
import { AnalyzeService } from '../services/analyze.service.js';
import { DouyinService } from '../services/douyin.service.js';
import { XiaohongshuService } from '../services/xiaohongshu.service.js';
import { ResponseFormatter } from '../utils/response.js';
import { createLogger } from '../utils/logger.js';
import { config } from '../utils/config.js';

const logger = createLogger('AnalyzeController');

export class AnalyzeController {
  /**
   * 通用分析接口
   */
  static async analyze(request: Request): Promise<Response> {
    try {
      const body = await request.json() as AnalyzeRequest;
      const result = await AnalyzeService.analyze(body);
      
      return new Response(JSON.stringify(result), {
        status: result.code === 200 ? 200 : 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    } catch (error) {
      logger.error('通用分析接口错误', error);
      const errorResponse = ResponseFormatter.error('请求处理失败');
      
      return new Response(JSON.stringify(errorResponse), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }

  /**
   * 抖音专用分析接口
   */
  static async analyzeDouyin(request: Request): Promise<Response> {
    try {
      const body = await request.json() as AnalyzeRequest;
      
      if (!body.url || body.url.trim() === '') {
        const errorResponse = ResponseFormatter.error('请提供有效的抖音链接');
        return new Response(JSON.stringify(errorResponse), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      const douyinService = new DouyinService(body.url, body.type);
      const result = await douyinService.analyze();
      const response = ResponseFormatter.success(result, '获取成功');
      
      return new Response(JSON.stringify(response), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    } catch (error) {
      logger.error('抖音分析接口错误', error);
      const errorMessage = error instanceof Error ? error.message : '抖音链接解析失败';
      const errorResponse = ResponseFormatter.error(errorMessage);
      
      return new Response(JSON.stringify(errorResponse), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }

  /**
   * 小红书专用分析接口
   */
  static async analyzeXiaohongshu(request: Request): Promise<Response> {
    try {
      const body = await request.json() as AnalyzeRequest;
      
      if (!body.url || body.url.trim() === '') {
        const errorResponse = ResponseFormatter.error('请提供有效的小红书链接');
        return new Response(JSON.stringify(errorResponse), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      const xiaohongshuService = new XiaohongshuService(body.url, body.type);
      const result = await xiaohongshuService.analyze();
      const response = ResponseFormatter.success(result, '获取成功');
      
      return new Response(JSON.stringify(response), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    } catch (error) {
      logger.error('小红书分析接口错误', error);
      const errorMessage = error instanceof Error ? error.message : '小红书链接解析失败';
      const errorResponse = ResponseFormatter.error(errorMessage);
      
      return new Response(JSON.stringify(errorResponse), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }

  /**
   * 健康检查接口
   */
  static async health(request: Request): Promise<Response> {
    const healthData: HealthResponse = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: config.environment
    };

    return new Response(JSON.stringify(healthData), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }

  /**
   * 处理OPTIONS请求（CORS预检）
   */
  static async options(request: Request): Promise<Response> {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400'
      }
    });
  }
}