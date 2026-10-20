# Redis 学习手册：从数据结构到生产实践

一本面向有编程基础读者的原创中文 Redis 学习书，包含 20 章、前言与参考附录。以 Redis 7.2 为实验基线，讲清数据结构、持久化、复制、高可用、缓存一致性、锁、消息消费、性能与运维，并提供可运行的库存预留项目。

**[在线阅读](https://aias00.github.io/redis-book/)** · **[下载 EPUB](https://aias00.github.io/redis-book/downloads/redis-learning-handbook.epub)** · [书稿](manuscript/00-preface.md)

## 内容

| 部分 | 章节 |
| --- | --- |
| 基础 | 1 环境，2 键与 TTL，3 String，4 集合建模，5 排行与统计，6 客户端 |
| 可靠性 | 7 事务与 Lua，8 内存，9 持久化，10 复制，11 Sentinel，12 Cluster |
| 实践 | 13 缓存一致性，14 锁与限流，15 Stream，16 性能，17 安全，18 运维 |
| 综合 | 19 幂等库存预留，20 练习答案，附录官方参考资料 |

在线版支持章节导航、全文搜索、深浅主题、手机阅读和继续上次阅读。阅读不依赖外部 CDN；EPUB 可使用 Apple Books、Calibre 等阅读器打开。

## 本地阅读与构建

生成文件已提交，直接预览无需安装 Python 依赖或 Pandoc：

```sh
python3 -m http.server 8000 --directory docs
```

访问 `http://127.0.0.1:8000`。修改 `manuscript/*.md` 后，用 Python 3.10+ 和 **Pandoc 3.12.1** 构建（构建脚本仅使用 Python 标准库）：

```sh
python3 scripts/build.py
python3 scripts/verify.py
```

输出 `downloads/redis-learning-handbook.epub` 和 `docs/` 网站。同一书稿生成两种格式；EPUB 含封面、中文元数据和分章目录。中文翻译文件在 `assets/pandoc/translations/zh.yaml`。

## 运行实验

需要 Docker 和 Compose 插件，以及未被占用的本机 6379 端口：

```sh
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python examples/pipeline.py
python examples/reserve.py --reset
python -m unittest discover -s tests -v
```

默认连接 `redis://127.0.0.1:6379/0`，可用 `REDIS_URL` 覆盖。所有实验仅用于独立实例。测试使用随机键前缀；库存演示的 `--reset` 会重置专用的 `book:{sku:demo}:` 命名空间。默认 Compose 是单实例，Sentinel 和 Cluster 章节说明原理及部署边界，不把单实例实验声称为集群演练。

停止实验：`docker compose down`。命名卷保留数据，添加 `--volumes` 才删除它。

## 验证与发布

- `scripts/verify.py` 检查章节覆盖、源文件摘要、HTML 内部链接、资源、EPUB 包结构、XML、语言与 spine。
- 集成测试验证 TTL、事务运行时错误、限流、幂等预留和并发不超卖。
- GitHub Actions 验证书稿产物，重建，使用 EPUBCheck 5.3.0 校验，并部署 `docs/` 至 Pages；PR 只验证。
- 仓库 Pages 来源为 **GitHub Actions**，`main` 推送后自动更新阅读站。

[验证记录](docs/validation.md) 包含实际执行范围；分布式故障与生产容量需要在目标环境另行验证。

## 许可

书稿、封面与排版文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，署名“Redis 学习手册编写组”，引用时链接本仓库。示例、构建和测试代码采用 [MIT](LICENSE-CODE)。Redis 是相关权利人的商标，本项目不是官方出版物。
