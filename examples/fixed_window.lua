local ttl = tonumber(ARGV[1])
if not ttl or ttl < 1 or ttl > 604800 or ttl % 1 ~= 0 then
  return redis.error_reply('ttl must be an integer between 1 and 604800')
end
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ttl) end
return n
