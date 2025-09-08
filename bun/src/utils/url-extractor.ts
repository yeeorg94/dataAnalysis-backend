/**
 * URL提取工具类
 * 从文本中提取URL，支持各种格式的分享链接
 */
export class UrlExtractor {
  /**
   * 从文本中提取URL
   * @param text 包含URL的文本
   * @returns 提取的URL或null
   */
  static extractUrl(text: string): string | null {
    try {
      // 如果输入就是一个URL，直接返回
      if (text.startsWith('http://') || text.startsWith('https://')) {
        console.log(`输入已是URL: ${text}`);
        return text;
      }

      // 否则在文本中查找URL
      // 将中文逗号替换为空格，以便更好地分隔
      const tmp = text.replace(/，/g, ' ').replace(/,/g, ' ');

      // 首先尝试查找完整的HTTP/HTTPS URL
      const urlRegex = /https?:\/\/[^\s]+/;
      const match = tmp.match(urlRegex);
      
      if (match && match[0]) {
        let url = match[0];
        // 移除URL末尾可能的标点符号和反引号
        url = url.replace(/[.,;:!?)`]+$/, '');
        console.log(`从文本中提取到URL: ${url}`);
        return url;
      }

      // 如果没找到完整URL，尝试查找抖音短链接格式
      const douyinShortRegex = /([a-zA-Z0-9]{3,}):\s*\/\s*/;
      const douyinMatch = tmp.match(douyinShortRegex);
      if (douyinMatch && douyinMatch[1]) {
        const shortCode = douyinMatch[1];
        const url = `https://v.douyin.com/${shortCode}`;
        console.log(`从抖音分享文本中提取到短链接: ${url}`);
        return url;
      }

      // 尝试查找小红书短链接格式
      const xiaohongshuShortRegex = /([a-zA-Z0-9]{11})/;
      const xiaohongshuMatch = tmp.match(xiaohongshuShortRegex);
      if (xiaohongshuMatch && xiaohongshuMatch[1]) {
        const shortCode = xiaohongshuMatch[1];
        const url = `https://xhslink.com/${shortCode}`;
        console.log(`从小红书分享文本中提取到短链接: ${url}`);
        return url;
      }

      console.warn(`在文本中未找到URL: ${text}`);
      return null;
    } catch (error) {
      console.error(`提取URL时出错: ${error}`);
      return null;
    }
  }

  /**
   * 验证URL是否有效
   * @param url URL字符串
   * @returns 是否为有效URL
   */
  static isValidUrl(url: string): boolean {
    try {
      const urlObj = new URL(url);
      // 只允许HTTP和HTTPS协议
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  }
}