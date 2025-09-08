import { config } from './config.js';

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private static logLevelMap: Record<string, LogLevel> = {
    debug: LogLevel.DEBUG,
    info: LogLevel.INFO,
    warn: LogLevel.WARN,
    error: LogLevel.ERROR
  };

  private static currentLogLevel = this.logLevelMap[config.logLevel] || LogLevel.INFO;

  private static formatMessage(level: string, message: string, context?: any): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  private static shouldLog(level: LogLevel): boolean {
    return level >= this.currentLogLevel;
  }

  static debug(message: string, context?: any): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.log(this.formatMessage('debug', message, context));
    }
  }

  static info(message: string, context?: any): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.log(this.formatMessage('info', message, context));
    }
  }

  static warn(message: string, context?: any): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.formatMessage('warn', message, context));
    }
  }

  static error(message: string, error?: Error | any): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      const errorInfo = error instanceof Error ? {
        message: error.message,
        stack: error.stack
      } : error;
      console.error(this.formatMessage('error', message, errorInfo));
    }
  }
}

// 创建特定模块的日志器
export function createLogger(module: string) {
  return {
    debug: (message: string, context?: any) => Logger.debug(`[${module}] ${message}`, context),
    info: (message: string, context?: any) => Logger.info(`[${module}] ${message}`, context),
    warn: (message: string, context?: any) => Logger.warn(`[${module}] ${message}`, context),
    error: (message: string, error?: Error | any) => Logger.error(`[${module}] ${message}`, error)
  };
}