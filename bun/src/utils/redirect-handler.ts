import { createLogger } from './logger.js';

const logger = createLogger('RedirectHandler');

/**
 * 获取真实地址，处理302重定向
 * @param url 原始URL
 * @returns 重定向后的真实URL
 */
export async function getRealAddress(url: string): Promise<string> {
  try {
    const response = await fetch(url, {
      method: 'HEAD',
      redirect: 'manual', // 不自动跟随重定向
      headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
      }
    });

    // 如果是重定向状态码，返回Location头中的URL
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get('location');
      if (location) {
        logger.info(`重定向: ${url} -> ${location}`);
        return location;
      }
    }

    // 如果没有重定向，返回原URL
    return url;
  } catch (error) {
    logger.error(`获取真实地址失败: ${url}`, error);
    return url; // 出错时返回原URL
  }
}

/**
 * 白名单域名列表
 */
export const DOWNLOAD_FILE_URLS = [
  'https://txmov2.a.yximgs.com',
  'https://v1-cold.douyinvod.com',
  'https://v1-y.douyinvod.com',
  'https://v1.douyinvod.com',
  'https://v11-x.douyinvod.com',
  'https://v11.douyinvod.com',
  'https://v26-cold.douyinvod.com',
  'https://v26.douyinvod.com',
  'https://v29-cold.douyinvod.com',
  'https://v29.douyinvod.com',
  'https://v3-a.douyinvod.com',
  'https://v3-b.douyinvod.com',
  'https://v3-c.douyinvod.com',
  'https://v3-cold.douyinvod.com',
  'https://v3-d.douyinvod.com',
  'https://v3-e.douyinvod.com',
  'https://v3-x.douyinvod.com',
  'https://v3-y.douyinvod.com',
  'https://v3-z.douyinvod.com',
  'https://v5-cold.douyinvod.com',
  'https://v5-coldb.douyinvod.com',
  'https://v5-coldc.douyinvod.com',
  'https://v5-coldy.douyinvod.com',
  'https://v5-e.douyinvod.com',
  'https://v5-f.douyinvod.com',
  'https://v5-g.douyinvod.com',
  'https://v5-h.douyinvod.com',
  'https://v5-i.douyinvod.com',
  'https://v5-j.douyinvod.com',
  'https://v6-cold.douyinvod.com',
  'https://v6-x.douyinvod.com',
  'https://v6-y.douyinvod.com',
  'https://v6-z.douyinvod.com',
  'https://v6.douyinvod.com',
  'https://v83-c.douyinvod.com',
  'https://v83-d.douyinvod.com',
  'https://v83-x.douyinvod.com',
  'https://v83-y.douyinvod.com',
  'https://v83-z.douyinvod.com',
  'https://v83.douyinvod.com',
  'https://v9-cold.douyinvod.com',
  'https://v9-x.douyinvod.com',
  'https://v9-z.douyinvod.com',
  'https://v9.douyinvod.com',
  'https://v95.douyinvod.com',
  'https://v95-sz-cold.douyinvod.com'
];

/**
 * 检查URL是否在白名单域名中
 * @param url 要检查的URL
 * @returns 是否在白名单中
 */
export function isUrlInWhitelist(url: string): boolean {
  // 将https转换为http进行匹配
  const httpUrls = DOWNLOAD_FILE_URLS.map(u => u.replace('https', 'http'));
  
  return httpUrls.some(whitelistUrl => {
    // 提取域名部分进行匹配
    const whitelistDomain = whitelistUrl.replace('http://', '').replace('https://', '');
    return url.includes(whitelistDomain);
  });
}

/**
 * 重试获取白名单中的真实地址
 * @param playAddress 播放地址
 * @param maxRetries 最大重试次数，默认5次
 * @returns 最终的真实地址
 */
export async function getWhitelistRealAddress(playAddress: string, maxRetries: number = 5): Promise<string> {
  let currentAddress = playAddress;
  let tryCount = 0;
  
  logger.info(`开始获取白名单真实地址: ${playAddress}`);
  
  for (let i = 0; i < maxRetries; i++) {
    tryCount++;
    
    try {
      const realAddress = await getRealAddress(currentAddress);
      logger.info(`第${tryCount}次尝试，获取到地址: ${realAddress}`);
      
      // 检查是否在白名单中
      if (isUrlInWhitelist(realAddress)) {
        logger.info(`找到白名单地址: ${realAddress}`);
        return realAddress;
      }
      
      // 如果不在白名单中，继续用这个地址重试
      currentAddress = realAddress;
      
    } catch (error) {
      logger.error(`第${tryCount}次尝试失败:`, error);
    }
  }
  
  logger.warn(`重试${maxRetries}次后仍未找到白名单地址，返回最后获取的地址: ${currentAddress}`);
  return currentAddress;
}