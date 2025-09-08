import { XiaohongshuService } from './src/services/xiaohongshu.service.js';
import { createLogger } from './src/utils/logger.js';

const logger = createLogger('Debug');

async function debugSpecificLink() {
  const url = 'http://xhslink.com/m/4BuZdKfWz7P';
  
  try {
    logger.info('开始调试特定链接:', url);
    
    // 获取页面内容
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
      },
      redirect: 'follow'
    });
    
    const html = await response.text();
    logger.info('页面内容长度:', html.length);
    logger.info('最终URL:', response.url);
    
    // 查找所有script标签
    const scriptMatches = html.match(/<script[^>]*>([\s\S]*?)<\/script>/gi);
    if (scriptMatches) {
      logger.info(`找到 ${scriptMatches.length} 个script标签`);
      
      scriptMatches.forEach((script, index) => {
        if (script.includes('__INITIAL_STATE__')) {
          logger.info(`script标签 ${index} 包含 __INITIAL_STATE__`);
          
          // 提取数据
          const match = script.match(/window\.__INITIAL_STATE__\s*=\s*({[\s\S]*?});?\s*<\/script>/i);
          if (match) {
            try {
              const jsonStr = match[1].replace(/undefined/g, 'null');
              const data = JSON.parse(jsonStr);
              
              logger.info('成功解析 __INITIAL_STATE__');
              
              // 打印整个数据结构的顶层键
              logger.info('数据顶层键:', Object.keys(data));
              
              // 检查数据结构
              if (data.root) {
                logger.info('找到 root，键:', Object.keys(data.root));
                
                if (data.root.noteData) {
                  logger.info('找到 root.noteData，键:', Object.keys(data.root.noteData));
                  
                  // 检查 normalNotePreloadData
                  if (data.root.noteData.normalNotePreloadData) {
                    const preloadData = data.root.noteData.normalNotePreloadData;
                    logger.info('normalNotePreloadData 结构:');
                    logger.info('- 键:', Object.keys(preloadData));
                    logger.info('- title:', preloadData.title || 'undefined');
                    logger.info('- desc:', preloadData.desc || 'undefined');
                    logger.info('- imagesList 类型:', typeof preloadData.imagesList);
                    logger.info('- imagesList 长度:', preloadData.imagesList ? Object.keys(preloadData.imagesList).length : 0);
                    
                    if (preloadData.imagesList) {
                      logger.info('imagesList 内容:', JSON.stringify(preloadData.imagesList, null, 2));
                    }
                  } else {
                    logger.info('未找到 normalNotePreloadData');
                  }
                  
                  // 检查 data.noteData
                  if (data.root.noteData.data && data.root.noteData.data.noteData) {
                    const noteData = data.root.noteData.data.noteData;
                    logger.info('data.noteData 结构:');
                    logger.info('- 键:', Object.keys(noteData));
                    logger.info('- title:', noteData.title || 'undefined');
                    logger.info('- desc:', noteData.desc || 'undefined');
                    
                    if (noteData.imageList) {
                      logger.info('- imageList 长度:', noteData.imageList.length);
                      logger.info('- imageList 内容:', JSON.stringify(noteData.imageList, null, 2));
                    }
                  } else {
                    logger.info('未找到 data.noteData');
                  }
                } else {
                  logger.info('未找到 root.noteData');
                }
              } else {
                logger.info('未找到 root');
                
                // 检查新的数据结构
                if (data.noteData) {
                  logger.info('找到 noteData，键:', Object.keys(data.noteData));
                  
                  // 检查 normalNotePreloadData
                  if (data.noteData.normalNotePreloadData) {
                    const preloadData = data.noteData.normalNotePreloadData;
                    logger.info('normalNotePreloadData 结构:');
                    logger.info('- 键:', Object.keys(preloadData));
                    logger.info('- title:', preloadData.title || 'undefined');
                    logger.info('- desc:', preloadData.desc || 'undefined');
                    
                    // 检查图片相关字段
                    if (preloadData.imagesList) {
                      logger.info('- imagesList 类型:', typeof preloadData.imagesList);
                      logger.info('- imagesList 长度:', preloadData.imagesList ? Object.keys(preloadData.imagesList).length : 0);
                      logger.info('- imagesList 内容:', JSON.stringify(preloadData.imagesList, null, 2));
                    }
                    
                    if (preloadData.imageList) {
                      logger.info('- imageList 长度:', preloadData.imageList.length);
                      logger.info('- imageList 内容:', JSON.stringify(preloadData.imageList, null, 2));
                    }
                    
                    if (preloadData.images) {
                      logger.info('- images 类型:', typeof preloadData.images);
                      logger.info('- images 内容:', JSON.stringify(preloadData.images, null, 2));
                    }
                  } else {
                    logger.info('未找到 normalNotePreloadData');
                  }
                  
                  // 检查是否有其他图片相关数据
                  if (data.noteData.imageList) {
                    logger.info('noteData.imageList 长度:', data.noteData.imageList.length);
                    logger.info('noteData.imageList 内容:', JSON.stringify(data.noteData.imageList, null, 2));
                  }
                  
                  if (data.noteData.images) {
                    logger.info('noteData.images 类型:', typeof data.noteData.images);
                    logger.info('noteData.images 内容:', JSON.stringify(data.noteData.images, null, 2));
                  }
                }
              }
              
            } catch (parseError) {
              logger.error('解析JSON失败:', parseError);
            }
          }
        }
      });
    }
    
    // 使用服务解析
    logger.info('\n=== 使用XiaohongshuService解析 ===');
    const result = await XiaohongshuService.parseUrl(url);
    logger.info('解析结果:', JSON.stringify(result, null, 2));
    
  } catch (error) {
    logger.error('调试失败:', error);
  }
}

debugSpecificLink();