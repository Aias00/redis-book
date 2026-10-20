# 第 7 章　事务、乐观锁与 Lua 原子性

## 7.1 MULTI/EXEC 保证什么

```redis
MULTI
SET lab:tx:a 1
INCR lab:tx:a
GET lab:tx:a
EXEC
```

`MULTI` 后命令排队，`EXEC` 时按顺序执行，执行过程中不会插入其他客户端的命令。它不提供传统关系事务的回滚。排队时的语法错误可能导致整个事务无法提交；执行时的类型错误则只影响相应命令，其他命令仍会执行。

```redis
SET lab:tx:bad text
MULTI
INCR lab:tx:bad
SET lab:tx:ok yes
EXEC
GET lab:tx:ok
```

最后仍读到 `yes`。因此应在事务前进行参数与类型设计，不要依赖“出错后自动恢复到事务前”。

## 7.2 WATCH 检查并发变化

客户端 A 执行 `WATCH lab:balance`，再读取余额并计算新值；客户端 B 在 A 提交前修改同一键；A 的 `EXEC` 将返回空结果，表示事务因监视键变化而未执行。过期等变化也会影响 WATCH。

应用需要重新读取、重新计算并有界重试，不能拿旧计算结果无限提交。竞争激烈时，乐观锁可能持续冲突；简单条件修改更适合脚本。

## 7.3 首次计数时设置 TTL

以下脚本放在 `examples/fixed_window.lua`。只操作通过 `KEYS` 显式传入的键，并在写入前验证参数。TTL 限制为 1—604800 秒，避免超大参数在计数写入后才触发 EXPIRE 范围错误。

```lua
local ttl = tonumber(ARGV[1])
if not ttl or ttl < 1 or ttl > 604800 or ttl % 1 ~= 0 then
  return redis.error_reply('ttl must be an integer between 1 and 604800')
end
local n = redis.call('INCR', KEYS[1])
if n == 1 then
  redis.call('EXPIRE', KEYS[1], ttl)
end
return n
```

这是“从首次请求起计时”的固定窗口计数，不是按自然分钟对齐，也没有消除窗口交界突发。调用者把计数与阈值比较决定是否放行，拒绝请求也会计入本次计数。运行方式：

```sh
docker compose exec -T redis redis-cli EVAL "$(cat examples/fixed_window.lua)" 1 lab:limit 60
```

脚本运行期间其他命令不能插入，长循环会阻塞整个实例。脚本发生运行时错误也不会回滚先前写入，因此应把可预见的校验尽量放到第一次写入之前。

## 7.4 脚本缓存与部署

`EVALSHA` 可减少传输脚本文本，但脚本缓存可能因重启、切换或其他原因不存在。客户端需要处理 `NOSCRIPT` 并按库的机制加载。Redis Functions 自 7.0 提供另一种服务端代码管理方式，但它的部署、命名和权限仍需设计。

练习：解释 Pipeline、事务和 Lua 的区别。若脚本先 `DECR` 再检查参数，检查失败抛错，库存会恢复吗？如何重排步骤？
