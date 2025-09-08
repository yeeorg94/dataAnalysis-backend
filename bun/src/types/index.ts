// 请求参数类型
export interface AnalyzeRequest {
  url: string;
  type?: 'png' | 'webp';
  format?: 'json';
}

// 响应数据类型
export interface ApiResponse<T = any> {
  code: number;
  data: T | null;
  message: string;
}

// 媒体数据类型
export interface MediaData {
  url: string;
  final_url: string;
  title: string;
  description: string;
  image_list: string[];
  live_list?: string[]; // 小红书特有
  video: string;
  app_type: 'douyin' | 'xiaohongshu';
}

// 抖音数据结构
export interface DouyinVideoData {
  videoInfoRes: {
    item_list: Array<{
      desc: string;
      images?: Array<{ url_list: string[] }>;
      video?: {
        play_addr: {
          url_list: string[];
        };
      };
    }>;
  };
}

// 小红书数据结构
export interface XiaohongshuNoteData {
  note: {
    noteDetailMap: Record<string, {
      note: {
        imageList: Array<{
          urlDefault: string;
          stream?: {
            h264: Array<{ masterUrl: string }>;
          };
        }>;
        video?: {
          media: {
            stream: {
              h264: Array<{ masterUrl: string }>;
            };
          };
        };
      };
    }>;
    firstNoteId: string;
  };
}

// 配置类型
export interface AppConfig {
  host: string;
  port: number;
  environment: 'development' | 'production' | 'testing';
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  userAgents: {
    default: string;
    mobile: string;
  };
  appTypeKeywords: {
    xiaohongshu: string[];
    douyin: string[];
  };
}

// 健康检查响应类型
export interface HealthResponse {
  status: string;
  timestamp: string;
  environment: string;
}