import { describe, it, expect } from 'bun:test';
import { UrlExtractor } from '../src/utils/url-extractor.js';

describe('UrlExtractor', () => {
  describe('extractUrl', () => {
    it('应该直接返回HTTP URL', () => {
      const url = 'http://example.com';
      const result = UrlExtractor.extractUrl(url);
      expect(result).toBe(url);
    });

    it('应该直接返回HTTPS URL', () => {
      const url = 'https://example.com';
      const result = UrlExtractor.extractUrl(url);
      expect(result).toBe(url);
    });

    it('应该从文本中提取URL', () => {
      const text = '这是一个链接 https://www.douyin.com/video/123 请查看';
      const result = UrlExtractor.extractUrl(text);
      expect(result).toBe('https://www.douyin.com/video/123');
    });

    it('应该处理中文逗号分隔的文本', () => {
      const text = '分享链接，https://xiaohongshu.com/note/123，快来看看';
      const result = UrlExtractor.extractUrl(text);
      expect(result).toBe('https://xiaohongshu.com/note/123');
    });

    it('应该移除URL末尾的标点符号', () => {
      const text = '链接: https://example.com/path?param=1.';
      const result = UrlExtractor.extractUrl(text);
      expect(result).toBe('https://example.com/path?param=1');
    });

    it('对于无效文本应该返回null', () => {
      const text = '这里没有链接';
      const result = UrlExtractor.extractUrl(text);
      expect(result).toBeNull();
    });

    it('对于空字符串应该返回null', () => {
      const result = UrlExtractor.extractUrl('');
      expect(result).toBeNull();
    });
  });

  describe('isValidUrl', () => {
    it('应该验证有效的URL', () => {
      expect(UrlExtractor.isValidUrl('https://example.com')).toBe(true);
      expect(UrlExtractor.isValidUrl('http://example.com')).toBe(true);
      expect(UrlExtractor.isValidUrl('https://example.com/path?param=1')).toBe(true);
    });

    it('应该拒绝无效的URL', () => {
      expect(UrlExtractor.isValidUrl('not-a-url')).toBe(false);
      expect(UrlExtractor.isValidUrl('ftp://example.com')).toBe(false);
      expect(UrlExtractor.isValidUrl('')).toBe(false);
    });
  });
});