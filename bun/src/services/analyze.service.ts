import type { AnalyzeRequest, MediaData, ApiResponse } from '../types/index.js';
import { DouyinService } from './douyin.service.js';
import { XiaohongshuService } from './xiaohongshu.service.js';
import { UrlExtractor } from '../utils/url-extractor.js';
import { ResponseFormatter } from '../utils/response.js';
import { createLogger } from '../utils/logger.js';
import { config } from '../utils/config.js';

const logger = createLogger('AnalyzeService');

export class AnalyzeService {
  /**
   * 分析URL并返回媒体数据
   */
  static async analyze(request: AnalyzeRequest): Promise<ApiResponse<MediaData>> {
    try {
      const { url: inputUrl, type = 'png' } = request;
      
      if (!inputUrl || inputUrl.trim() === '') {
        return ResponseFormatter.error('请提供有效的文本或URL');
      }

      logger.info(`开始分析请求`, { url: inputUrl, type });
      
      // 提取URL
      const url = UrlExtractor.extractUrl(inputUrl);
      if (!url) {
        return ResponseFormatter.error('无法从提供的文本中提取有效的URL');
      }

      // 判断URL类型并调用相应的服务
      const urlType = this.determineUrlType(url);
      logger.info(`检测到URL类型: ${urlType}`);
      
      let result: MediaData;
      
      switch (urlType) {
        case 'douyin':
          const douyinService = new DouyinService(inputUrl, type);
          result = await douyinService.analyze();
          break;
          
        case 'xiaohongshu':
          const xiaohongshuService = new XiaohongshuService(inputUrl, type);
          result = await xiaohongshuService.analyze();
          break;
          
        default:
          return ResponseFormatter.error(`不支持的URL类型: ${urlType}`);
      }
      
      logger.info('分析完成', { app_type: result.app_type });
      return ResponseFormatter.success(result, '获取成功');
      
    } catch (error) {
      logger.error('分析过程中发生错误', error);
      const errorMessage = error instanceof Error ? error.message : '分析失败';
      return ResponseFormatter.error(errorMessage);
    }
  }

  /**
   * 判断URL类型
   */
  private static determineUrlType(url: string): string {
    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname.toLowerCase();
      
      // 检查抖音相关域名
      const douyinDomains = ['douyin.com', 'v.douyin.com', 'iesdouyin.com'];
      for (const domain of douyinDomains) {
        if (hostname.includes(domain)) {
          return 'douyin';
        }
      }
      
      // 检查小红书相关域名
      const xiaohongshuDomains = ['xiaohongshu.com', 'xhslink.com', 'xhs.link'];
      for (const domain of xiaohongshuDomains) {
        if (hostname.includes(domain)) {
          return 'xiaohongshu';
        }
      }
      
      // 如果都不匹配，返回unknown
      return 'unknown';
    } catch (error) {
      logger.error('判断URL类型时出错', error);
      return 'unknown';
    }
  }

  /**
   * 获取支持的平台列表
   */
  static getSupportedPlatforms(): string[] {
    return ['douyin', 'xiaohongshu'];
  }

  /**
   * 检查URL是否被支持
   */
  static isSupportedUrl(url: string): boolean {
    const urlType = this.determineUrlType(url);
    return urlType !== 'unknown';
  }
}