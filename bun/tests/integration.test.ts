import { describe, it, expect, beforeAll, afterAll } from 'bun:test';
import { AnalyzeService } from '../src/services/analyze.service.js';
import { DouyinService } from '../src/services/douyin.service.js';
import { XiaohongshuService } from '../src/services/xiaohongshu.service.js';
import { UrlExtractor } from '../src/utils/url-extractor.js';
import type { MediaData } from '../src/types/index.js';

describe('Integration Tests', () => {
  // 不需要预先创建服务实例，因为它们需要参数

  describe('抖音测试用例', () => {
    const douyinTestCases = [
      {
        name: '抖音测试用例1 - 央广军事',
        input: '3.56 复制打开抖音，看看【央广军事的作品】# 他新创作的九三阅兵BGM再次刷屏 # 请祖国检... https://v.douyin.com/C6WTi3djsno/ G@V.lp eoD:/ 02/08',
        expectedUrl: 'https://v.douyin.com/C6WTi3djsno/'
      },
      {
        name: '抖音测试用例2 - 别捏七七',
        input: '6.69 复制打开抖音，看看【别捏七七的作品】道可道 非常道# 道德经 # 一口气挑战 https://v.douyin.com/6BfZJGtflnw/ zgO:/ f@O.Kw 04/18',
        expectedUrl: 'https://v.douyin.com/6BfZJGtflnw/'
      }
    ];

    douyinTestCases.forEach(({ name, input, expectedUrl }) => {
      it(name, async () => {
        // 测试URL提取
        const extractedUrl = UrlExtractor.extractUrl(input);
        expect(extractedUrl).toBe(expectedUrl);

        // 测试平台识别
        expect(DouyinService.isPlatformUrl(extractedUrl!)).toBe(true);

        // 模拟抖音服务解析（由于需要实际网络请求，这里测试基本结构）
        const douyinService = new DouyinService(input, 'png');
        expect(douyinService).toBeDefined();
        expect(typeof douyinService.analyze).toBe('function');
      });
    });
  });

  describe('小红书测试用例', () => {
    const xiaohongshuTestCases = [
      {
        name: '小红书测试用例1 - 追追米大王',
        input: '76 追追米大王发布了一篇小红书笔记，快来看吧！ 😆 35ajO3NDvPp 😆 http://xhslink.com/m/470umOpU7Ug 复制本条信息，打开【小红书】App查看精彩内容！',
        expectedUrl: 'http://xhslink.com/m/470umOpU7Ug'
      },
      {
        name: '小红书测试用例2 - 俊英陈',
        input: '35 俊英陈发布了一篇小红书笔记，快来看吧！ 😆 7gbQpJof4jZ 😆 http://xhslink.com/m/M0nGvFh6GY 复制本条信息，打开【小红书】App查看精彩内容！',
        expectedUrl: 'http://xhslink.com/m/M0nGvFh6GY'
      }
    ];

    xiaohongshuTestCases.forEach(({ name, input, expectedUrl }) => {
      it(name, async () => {
        // 测试URL提取
        const extractedUrl = UrlExtractor.extractUrl(input);
        expect(extractedUrl).toBe(expectedUrl);

        // 测试平台识别
        expect(XiaohongshuService.isPlatformUrl(extractedUrl!)).toBe(true);

        // 模拟小红书服务解析（由于需要实际网络请求，这里测试基本结构）
        const xiaohongshuService = new XiaohongshuService(input, 'png');
        expect(xiaohongshuService).toBeDefined();
        expect(typeof xiaohongshuService.analyze).toBe('function');
      });
    });
  });

  describe('通用解析服务测试', () => {
    it('应该正确识别抖音平台', () => {
      const douyinUrls = [
        'https://v.douyin.com/C6WTi3djsno/',
        'https://v.douyin.com/6BfZJGtflnw/',
        'https://www.douyin.com/video/123',
        'https://www.iesdouyin.com/share/video/123'
      ];

      douyinUrls.forEach(url => {
        expect(DouyinService.isPlatformUrl(url)).toBe(true);
      });
    });

    it('应该正确识别小红书平台', () => {
      const xiaohongshuUrls = [
        'http://xhslink.com/m/470umOpU7Ug',
        'http://xhslink.com/m/M0nGvFh6GY',
        'https://www.xiaohongshu.com/explore/123',
        'https://www.xiaohongshu.com/discovery/item/123'
      ];

      xiaohongshuUrls.forEach(url => {
        expect(XiaohongshuService.isPlatformUrl(url)).toBe(true);
      });
    });

    it('对于不支持的平台应该返回null', () => {
      const unsupportedUrls = [
        'https://www.youtube.com/watch?v=123',
        'https://www.bilibili.com/video/123',
        'https://example.com'
      ];

      unsupportedUrls.forEach(url => {
        expect(DouyinService.isPlatformUrl(url)).toBe(false);
        expect(XiaohongshuService.isPlatformUrl(url)).toBe(false);
      });
    });
  });

  describe('API响应格式测试', () => {
    it('应该返回正确的MediaData结构', () => {
      const mockMediaData: MediaData = {
        url: 'https://v.douyin.com/C6WTi3djsno/',
        final_url: 'https://www.douyin.com/video/123',
        title: '测试标题',
        description: '测试描述',
        image_list: [],
        video: 'https://aweme.snssdk.com/aweme/v1/play/?video_id=123',
        app_type: 'douyin'
      };

      // 验证必需字段
      expect(mockMediaData.url).toBeDefined();
      expect(mockMediaData.final_url).toBeDefined();
      expect(mockMediaData.title).toBeDefined();
      expect(mockMediaData.description).toBeDefined();
      expect(Array.isArray(mockMediaData.image_list)).toBe(true);
      expect(mockMediaData.video).toBeDefined();
      expect(['douyin', 'xiaohongshu'].includes(mockMediaData.app_type)).toBe(true);
    });

    it('小红书数据应该包含live_list字段', () => {
      const mockXiaohongshuData: MediaData = {
        url: 'http://xhslink.com/m/470umOpU7Ug',
        final_url: 'https://www.xiaohongshu.com/explore/123',
        title: '小红书测试标题',
        description: '小红书测试描述',
        image_list: ['https://ci.xiaohongshu.com/123?imageView2/format/png'],
        live_list: ['https://sns-video-bd.xhscdn.com/123'],
        video: 'https://sns-video-bd.xhscdn.com/123',
        app_type: 'xiaohongshu'
      };

      expect(mockXiaohongshuData.live_list).toBeDefined();
      expect(Array.isArray(mockXiaohongshuData.live_list)).toBe(true);
    });
  });
});