local quantity = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
if not quantity or quantity < 1 or quantity > 1000000000 or quantity % 1 ~= 0 then
  return redis.error_reply('invalid quantity')
end
if not ttl or ttl < 1 or ttl > 604800 or ttl % 1 ~= 0 then
  return redis.error_reply('invalid ttl')
end
local stock_type = redis.call('TYPE', KEYS[1]).ok
local request_type = redis.call('TYPE', KEYS[2]).ok
if stock_type ~= 'string' or (request_type ~= 'none' and request_type ~= 'string') then
  return redis.error_reply('invalid key type')
end
local prior = redis.call('GET', KEYS[2])
if prior then
  local saved_quantity, status, remaining = string.match(prior, '^(%d+)|(%d)|(%d+)$')
  if not saved_quantity then return redis.error_reply('invalid request record') end
  if tonumber(saved_quantity) ~= quantity then return redis.error_reply('request conflict') end
  return {tonumber(status), tonumber(remaining)}
end
local raw = redis.call('GET', KEYS[1])
local stock = tonumber(raw)
if not stock or not string.match(raw, '^%d+$') or stock > 1000000000 then
  return redis.error_reply('invalid stock')
end
local status = 0
local remaining = stock
if stock >= quantity then
  remaining = stock - quantity
  status = 1
end
-- Validate and construct the result before performing writes.
local result = string.format('%d|%d|%d', quantity, status, remaining)
if status == 1 then redis.call('DECRBY', KEYS[1], quantity) end
redis.call('SET', KEYS[2], result, 'EX', ttl)
return {status, remaining}
