# 视频去水印服务 (TypeScript版)

基于 Bun + TypeScript 重构的视频去水印服务，支持抖音和小红书平台的链接解析和媒体内容提取。

## 功能特性

- 🎯 **多平台支持**: 抖音、小红书
- 🚀 **高性能**: 基于 Bun 运行时
- 📝 **TypeScript**: 完整的类型安全
- 🧪 **TDD开发**: 测试驱动开发
- 🌐 **RESTful API**: 标准化接口设计
- 📊 **结构化日志**: 完整的日志记录
- 🔧 **配置管理**: 多环境配置支持

## 技术栈

- **运行时**: Bun
- **语言**: TypeScript
- **HTTP服务**: Bun内置服务器
- **HTML解析**: Cheerio
- **测试框架**: Bun Test

## 项目结构

```
bun/
├── src/
│   ├── controllers/     # 控制器层
│   │   └── analyze.controller.ts
│   ├── services/        # 服务层
│   │   ├── analyze.service.ts
│   │   ├── douyin.service.ts
│   │   └── xiaohongshu.service.ts
│   ├── utils/          # 工具类
│   │   ├── config.ts
│   │   ├── logger.ts
│   │   ├── response.ts
│   │   └── url-extractor.ts
│   └── types/          # 类型定义
│       └── index.ts
├── tests/              # 测试文件
├── index.ts           # 应用入口
├── package.json
└── tsconfig.json
```

## 快速开始

### 环境要求

- Bun >= 1.0.0
- Node.js >= 18.0.0 (可选，用于npm包管理)

### 安装依赖

```bash
# 使用 bun (推荐)
bun install

# 或使用 npm
npm install
```

### 启动服务

```bash
# 开发模式
bun run dev

# 生产模式
bun run start
```

### 运行测试

```bash
# 运行所有测试
bun test

# 监听模式
bun test --watch
```

## API 接口

### 健康检查

```http
GET /health
```

**响应示例:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "version": "1.0.0",
  "environment": "development",
  "supported_platforms": ["douyin", "xiaohongshu"]
}
```

### 通用分析接口

```http
POST /analyze
Content-Type: application/json

{
  "text": "分享链接或包含链接的文本",
  "type": "png"  // 可选: png, webp
}
```

### 抖音专用接口

```http
POST /analyze/douyin
Content-Type: application/json

{
  "text": "抖音分享链接",
  "type": "png"
}
```

### 小红书专用接口

```http
POST /analyze/xiaohongshu
Content-Type: application/json

{
  "text": "小红书分享链接",
  "type": "png"
}
```

**成功响应示例:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "url": "原始URL",
    "final_url": "最终URL",
    "title": "内容标题",
    "description": "内容描述",
    "image_list": ["图片URL1", "图片URL2"],
    "video": "视频URL",
    "app_type": "douyin"
  }
}
```

**错误响应示例:**
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

## 配置说明

### 环境变量

- `NODE_ENV`: 环境类型 (development/production/test)
- `PORT`: 服务端口 (默认: 3000)
- `HOST`: 服务主机 (默认: localhost)
- `LOG_LEVEL`: 日志级别 (debug/info/warn/error)

### 配置文件

配置文件位于 `src/utils/config.ts`，支持不同环境的配置:

- 开发环境: 详细日志，调试模式
- 生产环境: 优化性能，错误日志
- 测试环境: 测试专用配置

## 开发指南

### 添加新平台支持

1. 在 `src/types/index.ts` 中添加平台相关类型
2. 在 `src/services/` 中创建平台服务类
3. 在 `src/services/analyze.service.ts` 中添加平台判断逻辑
4. 在 `src/controllers/analyze.controller.ts` 中添加专用接口
5. 更新路由配置
6. 编写测试用例

### 代码规范

- 使用 TypeScript 严格模式
- 遵循 ESLint 规则
- 编写单元测试
- 使用结构化日志
- 错误处理要完整

### 测试策略

- 单元测试: 工具类、服务类
- 集成测试: API接口
- 端到端测试: 完整流程

## 部署

### Docker 部署

```dockerfile
FROM oven/bun:1-alpine

WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
EXPOSE 3000

CMD ["bun", "run", "start"]
```

### 生产环境配置

- 设置环境变量 `NODE_ENV=production`
- 配置反向代理 (Nginx)
- 设置进程管理 (PM2)
- 配置日志收集
- 设置监控告警

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持抖音和小红书平台
- 完整的 TypeScript 重构
- TDD 开发模式
