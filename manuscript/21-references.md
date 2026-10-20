# 附录　官方资料与命令速查

## 资料使用方法

本书以官方命令语义和运维文档为依据。以下链接指向持续更新的资料，访问日期为 2026-10-20；它们可能包含超出 Redis 7.2 基线的新增选项。使用前检查页面中的版本标记、目标服务版本和客户端支持，不要直接复制最新选项到旧实例。

| 主题 | 官方入口 | 对应章节 |
| --- | --- | --- |
| 数据结构 | <https://redis.io/docs/latest/develop/data-types/> | 3—5、15 |
| 命令检索与复杂度 | <https://redis.io/commands/> | 全书 |
| 过期语义 | <https://redis.io/commands/expire/> | 2、8 |
| SCAN 保证 | <https://redis.io/commands/scan/> | 2 |
| Pipeline | <https://redis.io/docs/latest/develop/using-commands/pipelining/> | 6 |
| 事务 | <https://redis.io/docs/latest/develop/using-commands/transactions/> | 7 |
| Lua 脚本 | <https://redis.io/docs/latest/develop/programmability/eval-intro/> | 7、19 |
| 内存淘汰 | <https://redis.io/docs/latest/develop/reference/eviction/> | 8 |
| 持久化 | <https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/> | 9 |
| 复制 | <https://redis.io/docs/latest/operate/oss_and_stack/management/replication/> | 10 |
| WAIT | <https://redis.io/commands/wait/> | 10 |
| Sentinel | <https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/> | 11 |
| Cluster 规范 | <https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/> | 12 |
| 分布式锁 | <https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/> | 14 |
| Stream | <https://redis.io/docs/latest/develop/data-types/streams/> | 15 |
| ACL | <https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/> | 17 |
| TLS | <https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/> | 17 |

## 命令速查

| 目的 | 命令 | 使用前想清楚 |
| --- | --- | --- |
| 条件缓存写入 | SET NX EX | 返回空值和超时不是同一种结果 |
| 批量读取 | MGET / HMGET | 返回体积、Cluster 槽约束 |
| 修改计数 | INCR / HINCRBY | 整数范围与重试幂等 |
| 游标遍历 | SCAN / HSCAN | 无快照、可能重复、游标到零 |
| 排行 | ZADD / ZRANGE | 同分规则与分数精度 |
| 回收大对象 | UNLINK | 异步释放积压 |
| 原子条件逻辑 | EVAL / EVALSHA | 前置校验、执行时长、缓存失效 |
| 观察复制 | INFO replication | 延迟和已落盘是不同概念 |
| 消费确认 | XACK | 不替代外部业务提交 |
| 查慢命令 | SLOWLOG GET | 不代表端到端延迟 |

## 建议的学习记录

为每个实验记录五项：版本与配置、预期结果、真实输出、失败边界、业务用途。每次结论写出适用条件，例如“在单主当前状态上原子执行”，避免把局部观察扩展成所有故障模型下的保证。
