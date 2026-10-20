# 第 5 章　Sorted Set 与概率统计结构

## 5.1 排行需要分数与成员

```redis
ZADD lab:rank 100 alice 80 bob 100 carol
ZINCRBY lab:rank 15 bob
ZRANGE lab:rank 0 -1 WITHSCORES
ZRANGE lab:rank 0 1 REV WITHSCORES
ZRANK lab:rank bob
```

成员唯一，分数可修改。默认按分数升序，分数相同再按成员的二进制字典序；`REV` 会反向排序。因此若业务要求同分者先达到者领先，必须显式设计规则。不能声称 Redis 自动按照提交时间打破同分。

分数使用双精度浮点数，连续整数在绝对值不超过 2^53 时可精确表达。将时间戳与分数随意拼成很大的整数，可能损失精度。复杂排名规则可在应用中二次排序，或者给明确上限的组合编码写出范围证明。

## 5.2 范围查询与窗口

```redis
ZADD lab:events 1000 e1 1010 e2 1020 e3
ZRANGE lab:events 1005 1020 BYSCORE
ZREMRANGEBYSCORE lab:events -inf 1005
ZCARD lab:events
```

这种模型可用于滑动时间窗口：删除窗口外成员，添加当前事件，统计窗口内数量。但三个独立命令之间会被其他客户端插入，需要原子脚本；事件成员还必须唯一，否则相同成员会更新而非新增。窗口内每次请求都保存一条记录，内存随流量增长，不能忽略容量上限。

## 5.3 HyperLogLog：用误差换空间

```redis
PFADD lab:uv user1 user2 user1
PFCOUNT lab:uv
PFADD lab:uv:next user2 user3
PFMERGE lab:uv:all lab:uv lab:uv:next
PFCOUNT lab:uv:all
```

HyperLogLog 估计去重基数，不支持枚举原始成员，也不适合删除单个用户。标准误差约 0.81%，这是统计性质，不是“每次结果都在固定误差范围内”的确定保证。小规模示例恰好精确，不说明大规模也精确。需要精确结算时用有审计能力的精确数据源。

## 5.4 地理位置

```redis
GEOADD lab:places 116.397 39.908 palace 116.407 39.904 center
GEODIST lab:places palace center km
GEOSEARCH lab:places FROMLONLAT 116.397 39.908 BYRADIUS 2 km WITHDIST ASC
```

经度在前，纬度在后。GEO 面向近似地理范围查询，不是路网导航系统，返回距离也不是实际驾车距离。基础地理结构由有序集合编码支撑，不支持给单个地点直接设置键级 TTL。

练习：全球日活统计和付费用户账单分别应选择什么结构？如果排行榜必须让同分者按最早达成时间排序，列出一种不损失精度的方案及代价。
