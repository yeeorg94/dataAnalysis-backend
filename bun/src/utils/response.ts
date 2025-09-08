import type { ApiResponse } from '../types/index.js';

export class ResponseFormatter {
  static readonly SUCCESS_CODE = 200;
  static readonly ERROR_CODE = 500;

  /**
   * 创建成功响应
   * @param data 响应数据
   * @param message 响应消息
   * @returns 格式化的成功响应
   */
  static success<T>(data: T, message: string = '获取成功'): ApiResponse<T> {
    return {
      code: this.SUCCESS_CODE,
      data,
      message
    };
  }

  /**
   * 创建错误响应
   * @param message 错误消息
   * @param code 错误代码，默认500
   * @returns 格式化的错误响应
   */
  static error(message: string, code: number = this.ERROR_CODE): ApiResponse<null> {
    return {
      code,
      data: null,
      message
    };
  }

  /**
   * 将响应转换为JSON字符串
   * @param response 响应对象
   * @returns JSON字符串
   */
  static toJson<T>(response: ApiResponse<T>): string {
    return JSON.stringify(response);
  }
}