import { AnalyzeController } from './src/controllers/analyze.controller.js';
import { createLogger } from './src/utils/logger.js';
import { config } from './src/utils/config.js';

const logger = createLogger('Server');

/**
 * 路由处理器
 */
async function handleRequest(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const { pathname, method } = { pathname: url.pathname, method: request.method };

  logger.info(`${method} ${pathname}`);

  // 处理CORS预检请求
  if (method === 'OPTIONS') {
    return AnalyzeController.options(request);
  }

  // 路由匹配
  switch (pathname) {
    case '/':
    case '/health':
      if (method === 'GET') {
        return AnalyzeController.health(request);
      }
      break;

    case '/analyze':
      if (method === 'POST') {
        return AnalyzeController.analyze(request);
      }
      break;

    case '/analyze/douyin':
      if (method === 'POST') {
        return AnalyzeController.analyzeDouyin(request);
      }
      break;

    case '/analyze/xiaohongshu':
      if (method === 'POST') {
        return AnalyzeController.analyzeXiaohongshu(request);
      }
      break;

    default:
      return new Response(JSON.stringify({
        code: 404,
        data: null,
        message: 'Not Found'
      }), {
        status: 404,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
  }

  // 方法不允许
  return new Response(JSON.stringify({
    code: 405,
    data: null,
    message: 'Method Not Allowed'
  }), {
    status: 405,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Allow': pathname === '/health' || pathname === '/' ? 'GET, OPTIONS' : 'POST, OPTIONS'
    }
  });
}

/**
 * 服务器配置
 */
const serverConfig = {
  port: config.port,
  hostname: config.host,
  fetch: handleRequest,
  error(error: Error) {
    logger.error('服务器错误', error);
    return new Response(JSON.stringify({
      code: 500,
      data: null,
      message: 'Internal Server Error'
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
};

logger.info(`🚀 视频去水印服务已启动`);
logger.info(`📍 服务地址: http://${config.host}:${config.port}`);
logger.info(`🌍 环境: ${config.environment}`);
logger.info(`📝 日志级别: ${config.logLevel}`);

export default serverConfig;