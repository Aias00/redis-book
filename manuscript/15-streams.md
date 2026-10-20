# 第 15 章　Pub/Sub、Stream 与可靠消费

## 15.1 实时广播与可恢复日志

Pub/Sub 将消息推送给当前在线的订阅者，断连期间的消息不会重放，适合允许丢失的在线提示。Stream 保存有序消息并允许按 ID 读取，消费组还提供待确认列表。二者不是把命令换个名字就能互相替代。

```redis
XADD lab:orders * order_id 42 status paid
XRANGE lab:orders - + COUNT 10
XGROUP CREATE lab:orders workers 0 MKSTREAM
XREADGROUP GROUP workers worker-a COUNT 10 STREAMS lab:orders >
```

首次执行创建组成功；重复创建同名组会报 `BUSYGROUP`，应用应明确处理。组从 `0` 建立，表示可读取此前已有消息；若从 `$` 建立，则从建组时的末尾以后开始。

## 15.2 待确认与接管

`XREADGROUP` 返回消息时，它会进入该消费组的 pending 状态。业务处理成功后，用返回的实际消息 ID 调用 `XACK`：

```text
XACK lab:orders workers <上一步返回的消息ID>
XPENDING lab:orders workers
XAUTOCLAIM lab:orders workers worker-b 60000 0-0 COUNT 10
```

尖括号是需要替换的说明，不是可直接执行的 ID。`XAUTOCLAIM` 可接管闲置足够久的 pending 消息。超时时间应覆盖正常处理时长，否则慢消费者和接管者可能重复处理同一业务。

## 15.3 至少一次需要幂等

消费者完成数据库写入后，在 `XACK` 前崩溃，消息会被再次处理。因此需要数据库唯一键或幂等结果表，以业务事件 ID 拒绝重复副作用。若先确认再处理，则可能丢失尚未执行的工作。只靠 Redis 消费组，无法自动让外部数据库写入实现恰好一次。

建议处理流程：读取消息；解析与校验；在数据库事务里写入事件去重记录及业务变更；提交成功后确认。失败则重试，超过次数转入死信并告警。重试次数、异常分类和死信重放都应有操作入口。

## 15.4 保留策略

Stream 不会因为确认就自动删除消息。需要使用有容量边界的裁剪或归档策略。过早裁剪可能让 pending 只剩引用而无法读取原始消息体，影响恢复。近似 `MAXLEN ~` 是性能与长度精度的折中，不能把近似上限当作精确内存配额。

练习：解释 `XACK`、删除消息和业务提交的关系。如果消息处理成功但确认响应丢失，消费者下一次该如何保证不会重复发货？
