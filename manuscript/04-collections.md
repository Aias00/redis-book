# 第 4 章　Hash、List 与 Set 的业务模型

## 4.1 Hash：把同一实体的字段放在一起

```redis
HSET lab:user:42 name Lin level 3
HGET lab:user:42 name
HMGET lab:user:42 name level missing
HINCRBY lab:user:42 level 1
HGETALL lab:user:42
```

Hash 适合用户摘要或配置字段，避免每改一个字段都序列化完整 JSON。在本书的 7.2 基线中，TTL 设置在整个键上，不能把新版本的字段级过期能力假设成基线能力。若字段需要独立过期，可拆键或由应用维护时间戳与清理流程。

不要把全体用户塞进单个超大 Hash：它会形成热键，并让迁移、全量读取与删除成本变大。`HGETALL` 返回全部字段，只适用于边界清晰的小对象；大对象渐进使用 `HSCAN`。

## 4.2 List：有序序列

```redis
LPUSH lab:tasks job1 job2
LRANGE lab:tasks 0 -1
RPOP lab:tasks
```

`LPUSH` 参数从左向右依次插入，因此首次读取列表应是 `job2, job1`，右端弹出 `job1`。选择哪端入队和哪端出队决定 FIFO 或 LIFO，不能只根据命令名猜测。

`BLPOP` 等阻塞命令可以等待新任务，但弹出后消费者崩溃会丢失待处理状态。可以用 `BLMOVE` 把任务原子移到处理中列表，再实现确认、超时回收；需求更复杂时使用 Stream。列表并不是默认可靠的消息系统。

## 4.3 Set：去重与集合计算

```redis
SADD lab:tag:redis u1 u2 u2
SADD lab:tag:database u2 u3
SCARD lab:tag:redis
SINTER lab:tag:redis lab:tag:database
SISMEMBER lab:tag:redis u1
```

集合成员唯一且无序，第一条新增数量是 2，交集包含 `u2`。Set 适合标签、关注关系和访问资格。大集合交并运算会消耗主线程时间，跨槽也有额外限制。用线上全集临时计算报表，可能拖慢延迟敏感请求。

## 4.4 选择由访问模式决定

如果只需要完整文档读取且更新稀少，String JSON 很自然；如果经常读写单字段，Hash 更合适；如果需要顺序和重复值，用 List；如果强调成员唯一性和存在性判断，用 Set。不要只按节省几个字节选模型，要把读写频率、单键大小、并发集中程度和清理方式一起比较。

练习：评论列表为什么不一定适合一个无限增长的 List？给出分页、归档与删除的模型。为“一个用户的最近 20 次访问”设计有界列表操作，并说明两个独立命令之间可能出现什么短暂状态。
