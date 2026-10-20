# 首版验证记录

日期：2026-10-20。该记录说明实际执行范围，不构成生产性能或故障恢复保证。

- 书稿：20 章、前言与参考附录，约 2.6 万中文字符（包含命令与标点）。
- 构建：Pandoc 3.12.1，Python 3.14；中文翻译补齐后以 `--fail-if-warnings` 完成 EPUB 3 和 HTML 构建。
- EPUBCheck 5.3.0：0 fatal、0 error、0 warning；通过 EPUB 3.3 规则校验。
- 结构验证：22 份书稿覆盖、源文件摘要、HTML 内部锚点与资源、EPUB XML、包内资源、中文元数据与阅读顺序通过。
- Redis：Docker 官方镜像 `redis:7.2`，实测服务端 7.2.16；镜像摘要 `sha256:46f15cf64fdef63e483dcda99e74e3d51c017b1175547b6bb874152ee2391aad`。
- 集成测试：10 项通过，涵盖 TTL 保留/覆盖、事务运行时错误不回滚、固定窗口正常及无效 TTL、幂等重试、拒绝稳定性、数量冲突、参数/类型失败无扣减、60 请求竞争 10 件库存、30 个相同请求只扣一次。
- 示例：100 条 Pipeline 写读通过；库存演示依次返回 `[1,7]`、`[1,7]`、`[0,7]`、请求冲突，最终库存 7。
- 浏览器：Chromium，桌面 1440×1000 与手机 390×844；章节目录、搜索、特殊字符安全处理、深浅主题、手机目录折叠、无水平溢出、无 JavaScript 错误、下载字节一致性通过。
- 参考文献：17 个 Redis 官方链接均经 HTTP 实际抓取成功；对事务、SCAN、淘汰、持久化、异步复制、WAIT 与 Sentinel 重点语义核对官方正文。
- 独立审阅：限流 TTL 上界与源/成品同步两项问题已修复，前者包含先失败后通过的回归验证。

未执行生产容量基准、掉电、磁盘损坏、Sentinel 自动切换或 Cluster 故障演练。书中相应章节明确了教学范围，默认实验环境是独立单实例。

可复查命令：

```sh
python3 scripts/build.py
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
java -jar /path/to/epubcheck.jar downloads/redis-learning-handbook.epub
```

GitHub Actions 会再次执行集成测试、检查、构建、EPUBCheck 并部署在线版，实际部署结果以仓库 Actions 和 Pages 地址为准。

## 线上验收

- GitHub 仓库：<https://github.com/Aias00/redis-book>，默认分支 `main`，公开可访问。
- 工作流 <https://github.com/Aias00/redis-book/actions/runs/39406031869> 对提交 `3f203e07eef745caa4562850583ffaf00964e8ac` 的验证及部署均成功，云端重复执行 10 项测试、构建与 EPUBCheck。
- 在线地址 <https://aias00.github.io/redis-book/> 实际返回成功，HTML 与本地成品逐字节一致；CSS、JavaScript 与 EPUB 下载均可访问。
- 下载 EPUB 的全部 22 个章节 XHTML 与仓库 EPUB 一致。云端重新构建会更新打包时间，因此未声称两个 ZIP 整体字节相同。
- 已在真实 Pages 地址执行手机视口 Chromium 检查：正文、搜索、目录跳转、无水平溢出及资源下载通过。
