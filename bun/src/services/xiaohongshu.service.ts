import * as cheerio from 'cheerio';
import type { MediaData, XiaohongshuNoteData } from '../types/index.js';
import { UrlExtractor } from '../utils/url-extractor.js';
import { ResponseFormatter } from '../utils/response.js';
import { createLogger } from '../utils/logger.js';
import { config } from '../utils/config.js';

const logger = createLogger('XiaohongshuService');

export class XiaohongshuService {
  private text: string;
  private type: string;
  private url: string | null;
  private description = '';
  private imageList: string[] = [];
  private liveList: string[] = [];
  private video = '';
  private title = '';
  private html = '';
  private finalUrl = '';
  private dataDict: any = {};

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
   * 解析小红书内容
   */
  async analyze(): Promise<MediaData> {
    try {
      logger.info(`开始解析小红书URL: ${this.url}`);
      
      // 处理重定向
      await this.handleRedirect();
      
      const headers = {
        'User-Agent': config.userAgents.mobile,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
      };

      const response = await fetch(this.finalUrl, {
        headers,
        redirect: 'follow'
      });

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status} - ${response.statusText}`);
      }

      this.html = await response.text();
      
      // 检查是否为404页面或错误页面 - 更精确的检测
      const isErrorPage = this.html.includes('404') || 
                         this.html.includes('页面不存在') || 
                         this.html.includes('页面未找到') ||
                         this.html.includes('内容不存在') ||
                         this.html.length < 500;
      
      // 检查是否包含小红书的关键元素
      const hasXhsElements = this.html.includes('__INITIAL_STATE__') || 
                            this.html.includes('xiaohongshu') ||
                            this.html.includes('小红书');
      
      if (isErrorPage && !hasXhsElements) {
        throw new Error(`小红书链接已失效或页面不存在: ${this.finalUrl}`);
      }
      
      logger.info(`获取到页面内容，长度: ${this.html.length}`);
      const $ = cheerio.load(this.html);
      
      // 提取页面标题
      this.title = $('title').text() || '';
      
      // 提取小红书数据
      await this.extractXiaohongshuData($);
      
      return this.toMediaData();
    } catch (error) {
      logger.error('获取小红书内容失败', error);
      throw error;
    }
  }

  /**
   * 处理URL重定向
   */
  private async handleRedirect(): Promise<void> {
    try {
      if (!this.url) {
        throw new Error('URL为空');
      }

      // 如果已经是最终URL，直接使用
      if (this.url.includes('xiaohongshu.com/explore/')) {
        this.finalUrl = this.url;
        return;
      }

      // 处理短链接重定向
      const headers = {
        'User-Agent': config.userAgents.mobile,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
      };

      const response = await fetch(this.url, {
        method: 'GET',
        redirect: 'follow',
        headers
      });

      this.finalUrl = response.url || this.url;
      logger.info(`重定向后的URL: ${this.finalUrl}`);
      
      // 检查是否为404页面 - 按照Python版本的逻辑
      if (this.finalUrl.includes('404')) {
        throw new Error(`小红书链接已失效: ${this.finalUrl}`);
      }
      
    } catch (error) {
      logger.warn('处理重定向失败，使用原始URL', error);
      this.finalUrl = this.url!;
    }
  }

  /**
   * 提取小红书内容
   */
  private async extractXiaohongshuData($: cheerio.CheerioAPI): Promise<void> {
    try {
      const scripts = $('script');
      
      for (let i = 0; i < scripts.length; i++) {
        const script = scripts.eq(i);
        const scriptContent = script.html();
        
        if (scriptContent && scriptContent.includes('window.__INITIAL_STATE__')) {
          // 提取 JSON 数据
          let dataText: string | undefined;
          try {
            dataText = scriptContent.split('window.__INITIAL_STATE__=')[1];
            
            // 找到JSON结束位置 - 使用更可靠的方法
            let endIndex = -1;
            let braceCount = 0;
            let inString = false;
            let escapeNext = false;
            
            for (let i = 0; i < dataText.length; i++) {
              const char = dataText[i];
              
              if (escapeNext) {
                escapeNext = false;
                continue;
              }
              
              if (char === '\\') {
                escapeNext = true;
                continue;
              }
              
              if (char === '"' && !escapeNext) {
                inString = !inString;
                continue;
              }
              
              if (!inString) {
                if (char === '{') {
                  braceCount++;
                } else if (char === '}') {
                  braceCount--;
                  if (braceCount === 0) {
                    endIndex = i + 1;
                    break;
                  }
                }
              }
            }
            
            if (endIndex !== -1) {
              dataText = dataText.substring(0, endIndex);
            }
            
            // 把字符串中的undefined替换为null
            const sanitizedDataText = dataText.replace(/undefined/g, 'null');
            
            this.dataDict = JSON.parse(sanitizedDataText);
            await this.parseInitialState(this.dataDict);
            break;
          } catch (error) {
            logger.warn('解析JSON数据失败', {
              error: error.message,
              dataLength: dataText?.length || 0,
              dataPreview: dataText?.substring(0, 200) || 'N/A'
            });

            continue;
          }
        }
      }
      

      // 如果没有找到数据，尝试获取meta description
      if (!this.description) {
        this.getMetaDescription($);
      }
    } catch (error) {
      logger.error('提取小红书数据失败:', error);
      throw error;
    }
  }

  /**
   * 获取页面的元描述
   */
  private getMetaDescription($: cheerio.CheerioAPI): void {
    try {
      const metaDesc = $('meta[name="description"]').attr('content') || 
                      $('meta[property="og:description"]').attr('content') || '';
      if (metaDesc) {
        this.description = metaDesc;
      }
    } catch (error) {
      logger.warn('获取meta描述失败', error);
    }
  }

  /**
   * 解析初始状态数据
   */
  private async parseInitialState(initialState: any): Promise<void> {
    try {
      // 尝试从不同的数据结构获取数据
      let noteData = {};
      let currentNoteData = {};
      
      // 检查新的数据结构：直接从initialState.noteData获取
      if (initialState.noteData) {
        noteData = initialState.noteData;
        
        // 从noteData.data.noteData获取笔记数据
        if (noteData.data && noteData.data.noteData) {
          currentNoteData = noteData.data.noteData;
        }
      } else {
        // 兼容旧版本：尝试从note字段获取数据
        const note = initialState.note || {};
        
        const noteDetailMap = note.noteDetailMap || {};
        const firstNoteId = note.firstNoteId || '';
        
        // 使用firstNoteId获取笔记数据
        if (firstNoteId && noteDetailMap[firstNoteId]) {
          currentNoteData = noteDetailMap[firstNoteId]?.note || {};
        } else {
          // 如果没有firstNoteId，取第一个可用的笔记
          const noteIds = Object.keys(noteDetailMap);
          if (noteIds.length > 0) {
            currentNoteData = noteDetailMap[noteIds[0]]?.note || {};
          }
        }
      }
      
      // 提取标题和描述 - 优先从normalNotePreloadData获取
      if (noteData.normalNotePreloadData) {
        this.title = noteData.normalNotePreloadData.title || currentNoteData.title || this.title;
        this.description = noteData.normalNotePreloadData.desc || currentNoteData.desc || this.description;
      } else {
        this.title = currentNoteData.title || this.title;
        this.description = currentNoteData.desc || this.description;
      }
      
      // 提取图片列表 - 检查多个数据源
      let imageList = [];
      let useCurrentNoteData = false;
      
      // 首先尝试从normalNotePreloadData.imagesList获取图片
      if (noteData.normalNotePreloadData?.imagesList) {
        imageList = noteData.normalNotePreloadData.imagesList;
      }
      
      // 如果normalNotePreloadData只有1张图片，也检查currentNoteData.imageList
      if (currentNoteData.imageList && currentNoteData.imageList.length > 0) {
        // 如果currentNoteData有更多图片，使用它
        if (currentNoteData.imageList.length > imageList.length) {
          imageList = currentNoteData.imageList;
          useCurrentNoteData = true;
        }
      }
      
      // 如果都没有，尝试其他可能的路径
      if (imageList.length === 0) {
        // 检查是否有其他可能的图片数据源
        if (noteData.data?.noteData?.imageList) {
          imageList = noteData.data.noteData.imageList;
        }
      }
      
      const images = imageList.map((img: any) => {
        // 优先使用无水印的URL格式
        // notes_pre_post 格式通常是无水印的，UUID格式可能带水印
        let imageUrl = '';
        
        // 检查是否有 notes_pre_post 格式的URL（无水印）
        if (img.urlSizeLarge && img.urlSizeLarge.includes('notes_pre_post')) {
          imageUrl = img.urlSizeLarge;
        } else if (img.url && img.url.includes('notes_pre_post')) {
          imageUrl = img.url;
        } else if (img.urlDefault && img.urlDefault.includes('notes_pre_post')) {
          imageUrl = img.urlDefault;
        } else {
          // 如果没有 notes_pre_post 格式，按原优先级选择
          imageUrl = img.urlSizeLarge || img.url || img.urlDefault;
          
          // 尝试将UUID格式转换为无水印格式
          if (imageUrl && this.isUuidFormat(imageUrl)) {
            const convertedUrl = this.tryConvertToNoWatermark(imageUrl);
            if (convertedUrl) {
              imageUrl = convertedUrl;
            }
          }
        }
        
        const liveUrl = img.livePhoto?.stream?.h264?.[0]?.masterUrl || img.stream?.h264?.[0]?.masterUrl || img.livePhoto || img.videoUrl;
        
        return {
          url: imageUrl,
          live_url: liveUrl || null
        };
      });
      
      this.imageList = images.map(img => img.url).filter(Boolean);
      this.liveList = images.map(img => img.live_url).filter(Boolean);
      
      // 处理视频 - 从stream.h264[0].masterUrl获取
      const videoInfo = currentNoteData?.video?.media || {};
      const masterUrl = videoInfo?.stream?.h264?.[0]?.masterUrl;
      if (masterUrl) {
        this.video = masterUrl;
      }
      
    } catch (error) {
      logger.error('解析初始状态数据失败', error);
      throw error;
    }
  }



  /**
   * 检查是否为UUID格式的URL
   */
  private isUuidFormat(url: string): boolean {
    // UUID格式：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    const uuidPattern = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
    return uuidPattern.test(url);
  }

  /**
   * 尝试将UUID格式的URL转换为无水印格式
   */
  private tryConvertToNoWatermark(url: string): string | null {
    try {
      // 如果URL已经包含imageView2参数，说明可能是无水印的
      if (url.includes('imageView2')) {
        return url;
      }
      
      // 为UUID格式的URL添加imageView2参数以获取无水印版本
      const separator = url.includes('?') ? '&' : '?';
      return `${url}${separator}imageView2/2/w/1080/format/jpg`;
    } catch (error) {
      logger.warn('转换URL格式失败', { url, error: error.message });
      return null;
    }
  }

  /**
   * 转换为MediaData格式
   */
  private toMediaData(): MediaData {
    return {
      url: this.url!,
      final_url: this.finalUrl,
      title: this.title,
      description: this.description,
      image_list: this.imageList,
      live_list: this.liveList,
      video: this.video,
      app_type: 'xiaohongshu'
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
   * 静态方法：检查是否为小红书链接
   */
  static isPlatformUrl(url: string): boolean {
    const xiaohongshuPatterns = [
      /xiaohongshu\.com/i,
      /xhslink\.com/i,
      /xhs\.link/i
    ];
    
    return xiaohongshuPatterns.some(pattern => pattern.test(url));
  }
}