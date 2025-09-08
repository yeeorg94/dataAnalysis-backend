import { describe, it, expect } from 'bun:test';
import { ResponseFormatter } from '../src/utils/response.js';
import type { ApiResponse } from '../src/types/index.js';

describe('ResponseFormatter', () => {
  describe('success', () => {
    it('应该创建成功响应', () => {
      const data = { id: 1, name: 'test' };
      const result = ResponseFormatter.success(data);
      
      expect(result.code).toBe(200);
      expect(result.data).toEqual(data);
      expect(result.message).toBe('获取成功');
    });

    it('应该支持自定义消息', () => {
      const data = { id: 1 };
      const message = '自定义成功消息';
      const result = ResponseFormatter.success(data, message);
      
      expect(result.code).toBe(200);
      expect(result.data).toEqual(data);
      expect(result.message).toBe(message);
    });

    it('应该处理null数据', () => {
      const result = ResponseFormatter.success(null);
      
      expect(result.code).toBe(200);
      expect(result.data).toBeNull();
      expect(result.message).toBe('获取成功');
    });
  });

  describe('error', () => {
    it('应该创建错误响应', () => {
      const message = '错误消息';
      const result = ResponseFormatter.error(message);
      
      expect(result.code).toBe(500);
      expect(result.data).toBeNull();
      expect(result.message).toBe(message);
    });

    it('应该支持自定义错误代码', () => {
      const message = '未找到';
      const code = 404;
      const result = ResponseFormatter.error(message, code);
      
      expect(result.code).toBe(code);
      expect(result.data).toBeNull();
      expect(result.message).toBe(message);
    });
  });

  describe('toJson', () => {
    it('应该将响应转换为JSON字符串', () => {
      const response: ApiResponse<any> = {
        code: 200,
        data: { test: 'value' },
        message: '成功'
      };
      
      const jsonString = ResponseFormatter.toJson(response);
      const parsed = JSON.parse(jsonString);
      
      expect(parsed).toEqual(response);
    });

    it('应该处理复杂数据结构', () => {
      const complexData = {
        array: [1, 2, 3],
        nested: {
          prop: 'value'
        },
        nullValue: null
      };
      
      const response = ResponseFormatter.success(complexData);
      const jsonString = ResponseFormatter.toJson(response);
      const parsed = JSON.parse(jsonString);
      
      expect(parsed.data).toEqual(complexData);
    });
  });
});