# 第 3 章　String：缓存、计数与条件写入

## 3.1 值是字节序列

String 可以保存 UTF-8 文本、JSON、整数的文本形式或二进制内容。Redis 不会替你检查 JSON 中字段是否符合业务约束。序列化格式需要约定版本、空值表现和兼容方式；应用升级后旧缓存仍可能存在。

```redis
SET lab:article:1 '{"v":1,"title":"认识 Redis"}' EX 300
GET lab:article:1
MSET lab:a 10 lab:b 20
MGET lab:a lab:b lab:missing
```

`MGET` 按请求顺序返回值，不存在的位置是空值。一次多键调用减少网络往返；在 Cluster 中，多键命令还必须满足同槽约束。

## 3.2 计数的原子边界

```redis
SET lab:views 0
INCR lab:views
INCRBY lab:views 9
GET lab:views
```

最终是 10。`INCR` 避免了客户端“读—加一—写”之间的竞争，它使用有符号 64 位整数，溢出会报错。浮点计数不适合精确货币；金额可用最小货币单位的整数表示，同时检查范围。

如果写成 `INCR` 后再 `EXPIRE`，两步之间进程可能失败，产生永不过期的计数键。用脚本把递增和首次过期放在一起，见第 7 章。

## 3.3 条件写入

```redis
SET lab:once first NX EX 30
SET lab:once second NX EX 30
GET lab:once
```

若初始键不存在，第一次成功，第二次返回空值，读到 `first`。`NX` 只在不存在时写，`XX` 只在存在时写。返回空值是条件未满足，并不等同于网络超时。

条件写入可以实现短期去重的占位，但“占位成功”并不代表后续业务已完成。业务失败后如何解除占位、重试是否会重复扣款、超时后结果能否查询，都需要额外协议。把去重当成完整的幂等实现会留下漏洞。

## 3.4 Bitmap 是位操作视角

```redis
SETBIT lab:attendance 7 1
GETBIT lab:attendance 7
BITCOUNT lab:attendance
```

偏移量以位计数。用户 ID 极大且稀疏时，直接作为位偏移会分配大量零填充空间；它适合稠密编号。按天保存签到位图，可通过位运算求连续活跃，但应控制键大小和运算成本。

练习：为什么“先 GET，不存在才 SET”无法保证只有一个客户端初始化？若某 API 超时，你能否根据超时推断 `INCR` 没有执行？给出安全的重试设计思路。
