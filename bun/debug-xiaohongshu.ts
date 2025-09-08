import { XiaohongshuService } from './src/services/xiaohongshu.service.js';
import { logger } from './src/utils/logger.js';

// 创建一个调试版本来测试图片提取逻辑
class DebugXiaohongshuService extends XiaohongshuService {
  // 重写extractXiaohongshuData方法，添加更详细的日志
  protected async extractXiaohongshuData($: any): Promise<void> {
    try {
      // 获取HTML内容用于调试
      const html = $.html();
      
      // 提取标题
      this.title = $('title').text() || '';
      console.log('提取到的标题:', this.title);
      
      // 输出HTML内容用于调试
      console.log('HTML类型:', typeof html);
      console.log('HTML内容长度:', html?.length || 0);
      console.log('HTML内容前1000字符:', html.substring(0, 1000));
      console.log('HTML内容后1000字符:', html.substring(Math.max(0, html.length - 1000)));
      
      // 查找所有script标签
      const scripts = $('script');
      console.log('找到script标签数量:', scripts.length);
      
      for (let i = 0; i < scripts.length; i++) {
        const script = scripts.eq(i);
        const scriptContent = script.html() || '';
        
        if (scriptContent.includes('window.__INITIAL_STATE__')) {
          console.log('找到包含__INITIAL_STATE__的script标签，索引:', i);
          console.log('Script内容长度:', scriptContent.length);
          console.log('Script内容前500字符:', scriptContent.substring(0, 500));
          
          // 提取 JSON 数据
          let dataText: string | undefined;
          try {
            dataText = scriptContent.split('window.__INITIAL_STATE__=')[1];
            console.log('分割后数据长度:', dataText?.length || 0);
            console.log('分割后数据前200字符:', dataText?.substring(0, 200) || 'N/A');
            
            // 找到JSON结束位置
            let endIndex = -1;
            let braceCount = 0;
            let inString = false;
            let escapeNext = false;
            
            for (let j = 0; j < dataText.length; j++) {
              const char = dataText[j];
              
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
                    endIndex = j + 1;
                    break;
                  }
                }
              }
            }
            
            if (endIndex !== -1) {
              dataText = dataText.substring(0, endIndex);
              console.log('JSON结束位置:', endIndex);
              console.log('最终JSON长度:', dataText.length);
            }
            
            // 替换undefined为null
            const sanitizedDataText = dataText.replace(/undefined/g, 'null');
            console.log('替换undefined后的数据长度:', sanitizedDataText.length);
            
            this.dataDict = JSON.parse(sanitizedDataText);
            console.log('JSON解析成功');
            console.log('数据结构键:', Object.keys(this.dataDict));
            
            // 分析数据结构
            this.analyzeDataStructure(this.dataDict);
            
            // 特别检查normalNotePreloadData中的imagesList
            if (this.dataDict.noteData?.normalNotePreloadData?.imagesList) {
              console.log('\n=== 发现normalNotePreloadData.imagesList ===');
              console.log('imagesList类型:', typeof this.dataDict.noteData.normalNotePreloadData.imagesList);
              console.log('imagesList长度:', this.dataDict.noteData.normalNotePreloadData.imagesList.length);
              console.log('imagesList内容:', JSON.stringify(this.dataDict.noteData.normalNotePreloadData.imagesList, null, 2));
            }
            
            await this.parseInitialState(this.dataDict);
            break;
          } catch (error) {
            console.error('解析JSON数据失败:', error.message);
            console.log('失败的数据长度:', dataText?.length || 0);
            console.log('失败的数据前200字符:', dataText?.substring(0, 200) || 'N/A');
            continue;
          }
        }
      }
      
      console.log('最终提取结果:');
      console.log('- 标题:', this.title);
      console.log('- 描述:', this.description);
      console.log('- 图片列表长度:', this.imageList.length);
      console.log('- 图片列表:', this.imageList);
      console.log('- Live列表长度:', this.liveList.length);
      console.log('- Live列表:', this.liveList);
      console.log('- 视频:', this.video);
      
    } catch (error) {
      console.error('提取小红书数据失败:', error);
      throw error;
    }
  }
  
  private analyzeDataStructure(data: any, path: string = 'root', depth: number = 0): void {
    if (depth > 3) return; // 限制深度避免过多输出
    
    if (typeof data === 'object' && data !== null) {
      const keys = Object.keys(data);
      console.log(`${' '.repeat(depth * 2)}${path}: {${keys.join(', ')}}`);
      
      // 重点关注可能包含图片数据的字段
      const imageRelatedKeys = keys.filter(key => 
        key.toLowerCase().includes('image') || 
        key.toLowerCase().includes('note') || 
        key.toLowerCase().includes('data') ||
        key.toLowerCase().includes('list')
      );
      
      imageRelatedKeys.forEach(key => {
        if (depth < 2) {
          this.analyzeDataStructure(data[key], `${path}.${key}`, depth + 1);
        }
      });
    }
  }
}

// 测试函数
async function testImageExtraction() {
  console.log('开始测试图片提取逻辑...');
  
  // 使用用户提供的小红书链接进行测试 - Groq+Kimi K2极速组合体验
  const testUrl = 'http://xhslink.com/m/4BuZdKfWz7P';
  
  try {
    const service = new DebugXiaohongshuService(testUrl, 'png');
    const result = await service.analyze();
    
    console.log('\n=== 最终分析结果 ===');
    console.log(JSON.stringify(result, null, 2));
    
  } catch (error) {
    console.error('测试失败:', error);
  }
}

// 运行测试
if (import.meta.main) {
  testImageExtraction();
}