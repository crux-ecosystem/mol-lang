# Concurrency

MOL has built-in concurrency with `spawn/await`, channels, and parallel utilities.

## Spawn & Await

Run code in a background thread:

```text
let task be spawn do
  sleep(100)
  "done!"
end

show "Main thread continues..."
let result be await task
show result    -- "done!"
```

`spawn` returns a task handle. `await` blocks until the task completes and returns its value.

## Multiple Tasks

```text
let t1 be spawn do
  sleep(50)
  "task A"
end

let t2 be spawn do
  sleep(30)
  "task B"
end

let t3 be spawn do
  sleep(10)
  "task C"
end

let results be wait_all([t1, t2, t3])
show results    -- ["task A", "task B", "task C"]
```

`wait_all` waits for all tasks and returns results in the **original order** (not completion order).

## Race

Get the result of whichever task finishes first:

```text
let fast be spawn do
  sleep(10)
  "fast wins!"
end

let slow be spawn do
  sleep(500)
  "slow loses"
end

let winner be race([fast, slow])
show winner    -- "fast wins!"
```

## Channels

Channels enable communication between tasks:

```text
let ch be channel()

-- Producer: sends messages
let producer be spawn do
  for i in range(5) do
    send(ch, f"message {i}")
    sleep(10)
  end
end

-- Consumer: receives messages
for i in range(5) do
  let msg be receive(ch)
  show msg
end

await producer
```

Output:
```text
message 0
message 1
message 2
message 3
message 4
```

## Parallel Map

Process a list in parallel using a thread pool:

```text
let items be [1, 2, 3, 4, 5, 6, 7, 8]

let results be parallel_map(items, fn(x) -> x * x)
show results    -- [1, 4, 9, 16, 25, 36, 49, 64]
```

!!! tip "When to use parallel_map"
    Best for CPU-bound or I/O-bound operations on lists. For simple math, the overhead of threads may not help.

## Mutex

Protect shared state with a mutex:

```text
let counter be 0
let lock be mutex()

let tasks be []
for i in range(10) do
  let t be spawn do
    lock_acquire(lock)
    set counter to counter + 1
    lock_release(lock)
  end
  push(tasks, t)
end

wait_all(tasks)
show counter    -- 10
```

## Patterns

### Fan-Out / Fan-In

```text
-- Process items in parallel, collect results
define fan_out(items, processor)
  let tasks be map(items, fn(item) ->
    spawn do
      processor(item)
    end
  )
  return wait_all(tasks)
end

let urls be ["url1", "url2", "url3"]
let responses be fan_out(urls, fn(url) ->
  f"fetched {url}"
end)
show responses
```

### Producer-Consumer Pipeline

```text
let ch be channel()

-- Multiple producers
for i in range(3) do
  spawn do
    for j in range(5) do
      send(ch, f"producer {i}: item {j}")
    end
  end
end

-- Single consumer
for i in range(15) do
  show receive(ch)
end
```

### Timeout Pattern

```text
let task be spawn do
  sleep(5000)
  "too slow"
end

let fast be spawn do
  sleep(100)
  "timeout"
end

let result be race([task, fast])
if result is "timeout" then
  show "Task timed out!"
end
```
