# 数据分析后端服务

这是一个基于 FastAPI 的综合性多媒体内容分析与处理 API 服务，支持社交媒体内容解析、证件照处理、图像修复、YouTube视频下载、用户行为埋点等功能。

## GitHub Actions CI/CD

本项目使用 GitHub Actions 进行持续集成和持续部署。工作流会在创建新的 Git 标签（以 `v` 开头）时自动触发，构建 Docker 镜像并推送到配置的 Docker 仓库。

### 配置 Secrets

为了使工作流正常运行，你需要在 GitHub 仓库的设置中配置以下 secrets：

1. `DOCKER_REGISTRY_SERVER_URL` - 你的 Docker 仓库服务器地址
2. `DOCKER_USERNAME` - 你的 Docker 仓库用户名
3. `DOCKER_PASSWORD` - 你的 Docker 仓库密码或访问令牌

### 触发构建

要触发构建和部署流程，请创建一个新的 Git 标签：

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

这将触发 GitHub Actions 工作流，构建 Docker 镜像并推送到你的 Docker 仓库，使用以下标签：
- `latest`
- Git commit SHA

### Docker 镜像

构建的 Docker 镜像将被推送到：
`$DOCKER_REGISTRY_SERVER_URL/xiaobe/counter_weapp`

你可以根据需要修改 `.github/workflows/ci-cd.yml` 中的镜像名称。