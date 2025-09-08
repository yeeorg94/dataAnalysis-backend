import * as cheerio from 'cheerio';
import type { MediaData, DouyinVideoData } from '../types/index.js';
import { UrlExtractor } from '../utils/url-extractor.js';
import { ResponseFormatter } from '../utils/response.js';
import { createLogger } from '../utils/logger.js';
import { config } from '../utils/config.js';

const logger = createLogger('DouyinService');

export class DouyinService {
  private text: string;
  private type: string;
  private url: string | null;
  private description = '';
  private imageList: string[] = [];
  private video = '';
  private title = '';
  private html = '';

  constructor(text: string, type: string = 'png') {
    this.text = text;
    this.type = type;
    this.url = UrlExtractor.extractUrl(text);
    
    if (!this.url) {
      const errorMsg = `无法从文本 '${text}' 中提取 URL`;
      logger.error(errorMsg);
      throw new Error(errorMsg);
    }
  }

  /**
   * 解析抖音内容
   */
  async analyze(): Promise<MediaData> {
    try {
      logger.info(`开始解析抖音URL: ${this.url}`);
      
      const headers = {
        'User-Agent': config.userAgents.mobile,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
      };

      const response = await fetch(this.url!, {
        headers,
        redirect: 'follow'
      });

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }

      this.html = await response.text();
      const $ = cheerio.load(this.html);
      
      // 提取页面标题
      this.title = $('title').text() || '';
      
      // 提取抖音数据
      await this.extractDouyinData($);
      
      return this.toMediaData();
    } catch (error) {
      logger.error('获取抖音内容失败', error);
      throw error;
    }
  }

  /**
   * 提取抖音内容
   */
  private async extractDouyinData($: cheerio.CheerioAPI): Promise<void> {
    try {
      const scripts = $('script');
      
      for (let i = 0; i < scripts.length; i++) {
        const script = scripts.eq(i);
        const scriptContent = script.html();
        
        if (scriptContent && scriptContent.includes('window._ROUTER_DATA')) {
          const dataText = scriptContent.split('window._ROUTER_DATA = ')[1];
          
          try {
            const routerData = JSON.parse(dataText);
            const loaderData = routerData.loaderData || {};
            
            // 判断有没有note_(id)/page, 没有的话取video_(id)/page
            let dataDict;
            if (dataText.includes('note_(id)')) {
              dataDict = loaderData['note_(id)/page'] || {};
            } else {
              dataDict = loaderData['video_(id)/page'] || {};
            }
            
            await this.parseDataDict(dataDict);
            break;
          } catch (parseError) {
            logger.warn('解析JSON数据失败', parseError);
            continue;
          }
        }
      }
    } catch (error) {
      logger.error('提取抖音数据失败', error);
      throw error;
    }
  }

  /**
   * 解析数据字典
   */
  private async parseDataDict(dataDict: any): Promise<void> {
    try {
      const videoInfoRes = dataDict.videoInfoRes || {};
      const itemList = videoInfoRes.item_list || [];
      const itemData = itemList[0] || {};
      
      this.description = itemData.desc || '';
      
      // 获取图片数据
      const images = itemData.images || [];
      if (images.length > 0) {
        this.parseImageData(images);
      }
      
      // 获取视频数据
      const video = itemData.video || {};
      if (Object.keys(video).length > 0) {
        this.parseVideoData(video);
      }
    } catch (error) {
      logger.error('解析数据字典失败', error);
      throw error;
    }
  }

  /**
   * 解析图片数据
   */
  private parseImageData(images: any[]): void {
    try {
      for (const image of images) {
        const urlList = image.url_list || [];
        if (urlList.length > 0) {
          this.imageList.push(urlList[0]);
        }
      }
    } catch (error) {
      logger.error('解析图片数据失败', error);
    }
  }

  /**
   * 解析视频数据
   */
  private parseVideoData(video: any): void {
    try {
      const playAddr = video.play_addr || {};
      const urlList = playAddr.url_list || [];
      
      if (urlList.length > 0) {
        let videoUrl = urlList[0];
        
        // 检查是否为mp3文件
        if (videoUrl.includes('mp3')) {
          this.video = '';
        } else {
          // 去水印处理：将playwm替换为play
          this.video = videoUrl.replace('playwm', 'play');
        }
      }
    } catch (error) {
      logger.error('解析视频数据失败', error);
    }
  }

  /**
   * 转换为MediaData格式
   */
  private toMediaData(): MediaData {
    return {
      url: this.url!,
      final_url: '',
      title: this.title,
      description: this.description,
      image_list: this.imageList,
      video: this.video,
      app_type: 'douyin'
    };
  }

  /**
   * 转换为API响应格式
   */
  toApiResponse() {
    try {
      const result = this.toMediaData();
      return ResponseFormatter.success(result, '获取成功');
    } catch (error) {
      logger.error('转换API响应格式失败', error);
      return ResponseFormatter.error('转换失败', 500);
    }
  }

  /**
   * 静态方法：检查是否为抖音链接
   */
  static isPlatformUrl(url: string): boolean {
    const douyinPatterns = [
      /douyin\.com/i,
      /v\.douyin\.com/i,
      /iesdouyin\.com/i
    ];
    
    return douyinPatterns.some(pattern => pattern.test(url));
  }
}