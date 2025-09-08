import { XiaohongshuService } from './src/services/xiaohongshu.service';
import * as cheerio from 'cheerio';
import fetch from 'node-fetch';
import { config } from './src/utils/config';

class DebugImageUrlService extends XiaohongshuService {
  public dataDict: any = null;
  public rawImageData: any[] = [];

  /**
   * 调试版本的数据提取方法
   */
  public async debugExtractData(): Promise<void> {
    try {
      // 处理重定向
      await this.handleRedirect();
      
      const headers = {
        'User-Agent': config.userAgents.mobile,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
      };

      const response = await fetch(this.finalUrl, {
        method: 'GET',
        headers,
        redirect: 'follow'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      this.html = await response.text();
      
      if (this.html.includes('404') || this.html.includes('页面不存在')) {
        throw new Error(`小红书链接已失效或页面不存在: ${this.finalUrl}`);
      }
      
      const $ = cheerio.load(this.html);
      
      // 提取页面标题
      this.title = $('title').text() || '';
      
      // 提取小红书数据
      await this.debugExtractXiaohongshuData($);
      
    } catch (error) {
      console.error('调试数据提取失败:', error);
      throw error;
    }
  }

  /**
   * 调试版本的小红书数据提取
   */
  private async debugExtractXiaohongshuData($: cheerio.CheerioAPI): Promise<void> {
    try {
      const scripts = $('script').toArray();
      
      for (const script of scripts) {
        const scriptContent = $(script).html();
        if (!scriptContent) continue;
        
        // 查找包含 window.__INITIAL_STATE__ 的脚本
        if (scriptContent.includes('window.__INITIAL_STATE__')) {
          console.log('\n=== 找到包含 __INITIAL_STATE__ 的脚本 ===');
          
          try {
            let dataText = scriptContent.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});?\s*(?:window|$)/s)?.[1];
            
            if (!dataText) {
              continue;
            }
            
            // 处理可能的不完整JSON
            let braceCount = 0;
            let endIndex = -1;
            
            for (let i = 0; i < dataText.length; i++) {
              const char = dataText[i];
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
            
            if (endIndex !== -1) {
              dataText = dataText.substring(0, endIndex);
            }
            
            // 把字符串中的undefined替换为null
            const sanitizedDataText = dataText.replace(/undefined/g, 'null');
            
            this.dataDict = JSON.parse(sanitizedDataText);
            
            console.log('\n=== 原始数据结构分析 ===');
            console.log('数据根键:', Object.keys(this.dataDict));
            
            // 分析图片数据结构
            await this.analyzeImageDataStructure();
            
            break;
          } catch (error) {
            console.warn('解析JSON数据失败:', error.message);
            continue;
          }
        }
      }
    } catch (error) {
      console.error('调试提取小红书数据失败:', error);
      throw error;
    }
  }

  /**
   * 分析图片数据结构
   */
  private async analyzeImageDataStructure(): Promise<void> {
    try {
      console.log('\n=== 分析图片数据结构 ===');
      
      // 检查新的数据结构：直接从initialState.noteData获取
      if (this.dataDict.noteData) {
        console.log('发现 noteData 结构');
        const noteData = this.dataDict.noteData;
        
        if (noteData.normalNotePreloadData?.imagesList) {
          console.log('\n--- normalNotePreloadData.imagesList ---');
          console.log('图片数量:', noteData.normalNotePreloadData.imagesList.length);
          
          noteData.normalNotePreloadData.imagesList.forEach((img: any, index: number) => {
            console.log(`\n图片 ${index + 1}:`);
            console.log('  - urlDefault:', img.urlDefault);
            console.log('  - url:', img.url);
            console.log('  - urlSizeLarge:', img.urlSizeLarge);
            console.log('  - 所有键:', Object.keys(img));
            
            this.rawImageData.push({
              index: index + 1,
              source: 'normalNotePreloadData.imagesList',
              data: img
            });
          });
        }
        
        if (noteData.data?.noteData?.imageList) {
          console.log('\n--- noteData.data.noteData.imageList ---');
          console.log('图片数量:', noteData.data.noteData.imageList.length);
          
          noteData.data.noteData.imageList.forEach((img: any, index: number) => {
            console.log(`\n图片 ${index + 1}:`);
            console.log('  - urlDefault:', img.urlDefault);
            console.log('  - url:', img.url);
            console.log('  - urlSizeLarge:', img.urlSizeLarge);
            console.log('  - 所有键:', Object.keys(img));
            
            this.rawImageData.push({
              index: index + 1,
              source: 'noteData.data.noteData.imageList',
              data: img
            });
          });
        }
      }
      
      // 检查旧版本数据结构
      if (this.dataDict.note) {
        console.log('\n发现 note 结构');
        const note = this.dataDict.note;
        const noteDetailMap = note.noteDetailMap || {};
        const firstNoteId = note.firstNoteId || '';
        
        if (firstNoteId && noteDetailMap[firstNoteId]) {
          const currentNoteData = noteDetailMap[firstNoteId]?.note || {};
          
          if (currentNoteData.imageList) {
            console.log('\n--- note.noteDetailMap[firstNoteId].note.imageList ---');
            console.log('图片数量:', currentNoteData.imageList.length);
            
            currentNoteData.imageList.forEach((img: any, index: number) => {
              console.log(`\n图片 ${index + 1}:`);
              console.log('  - urlDefault:', img.urlDefault);
              console.log('  - url:', img.url);
              console.log('  - urlSizeLarge:', img.urlSizeLarge);
              console.log('  - 所有键:', Object.keys(img));
              
              this.rawImageData.push({
                index: index + 1,
                source: 'note.noteDetailMap.imageList',
                data: img
              });
            });
          }
        }
      }
      
      // 分析URL格式差异
      this.analyzeUrlFormats();
      
    } catch (error) {
      console.error('分析图片数据结构失败:', error);
    }
  }

  /**
   * 分析URL格式差异
   */
  private analyzeUrlFormats(): void {
    console.log('\n=== URL格式分析 ===');
    
    const urlFormats = {
      'notes_pre_post': [],
      'direct_uuid': [],
      'other': []
    };
    
    this.rawImageData.forEach(item => {
      const img = item.data;
      const urls = [img.urlDefault, img.url, img.urlSizeLarge].filter(Boolean);
      
      urls.forEach(url => {
        if (url.includes('notes_pre_post')) {
          urlFormats['notes_pre_post'].push({ url, source: item.source, index: item.index });
        } else if (url.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/)) {
          urlFormats['direct_uuid'].push({ url, source: item.source, index: item.index });
        } else {
          urlFormats['other'].push({ url, source: item.source, index: item.index });
        }
      });
    });
    
    console.log('\n--- notes_pre_post 格式 ---');
    urlFormats['notes_pre_post'].forEach(item => {
      console.log(`图片${item.index} (${item.source}): ${item.url}`);
    });
    
    console.log('\n--- 直接UUID格式 ---');
    urlFormats['direct_uuid'].forEach(item => {
      console.log(`图片${item.index} (${item.source}): ${item.url}`);
    });
    
    console.log('\n--- 其他格式 ---');
    urlFormats['other'].forEach(item => {
      console.log(`图片${item.index} (${item.source}): ${item.url}`);
    });
  }
}

// 测试函数
async function debugImageUrls() {
  console.log('开始调试图片URL格式...');
  
  const testUrl = 'http://xhslink.com/m/44pFA7plEmT';
  
  try {
    const service = new DebugImageUrlService(testUrl, 'png');
    await service.debugExtractData();
    
    console.log('\n=== 调试完成 ===');
    
  } catch (error) {
    console.error('调试失败:', error);
  }
}

// 运行调试
debugImageUrls();