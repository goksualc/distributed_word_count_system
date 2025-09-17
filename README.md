Distributed Word Count System (Processes, Threads, RPC)

Overview

This project compares three implementation strategies for a small distributed system inspired by MapReduce. The chosen computational problem is: count word frequencies across multiple text files using three or more worker nodes. We implement and evaluate three variants:

- Process only: Parallelize with multiple OS processes on one machine
- Process + Threads: Hybrid fan-out where each process uses threads for intra-process parallelism
- RPC: Master/Worker over RPC to simulate multiple machines (workers on different ports)

Problem Definition

Given N text files, compute a global frequency map word -> count. Words are case-insensitive and defined as sequences of alphabetic characters (A–Z). Non-alphabetic characters are treated as delimiters.

High-Level MapReduce Design

- Map: For a chunk of text, tokenize into words and count occurrences locally
- Shuffle: Conceptually group counts of the same word; in this simplified implementation we merge partial dictionaries
- Reduce: Sum counts for identical words across all partial results

Pseudocode

Map(text_chunk):
  counts = empty dict<string,int>
  for w in tokenize(text_chunk.lower()):
    counts[w] += 1
  return counts

Reduce(dict_a, dict_b):
  for (w, c) in dict_b:
    dict_a[w] += c
  return dict_a

Driver(files, num_workers):
  chunks = split_each_file_into_chunks(files)
  partials = parallel_map(Map, chunks, num_workers)
  result = reduce_all(Reduce, partials)
  return result

Implementations

1) Process only

- Uses Python multiprocessing.Pool
- Parallelizes over file chunks across processes
- No threads used

2) Process + Threads

- Partitions chunks across multiple processes
- Each process uses a thread pool to map chunks concurrently
- Aggregation across processes via a manager queue / pipes

3) RPC (Master/Workers)

- Workers run xmlrpc servers on different ports (simulating different machines)
- Master splits input into chunks, distributes to workers via RPC calls
- Workers return partial maps; master merges them

Project Layout

- src/utils.py: Tokenization, chunking, merging, IO helpers
- src/process_only.py: Process-only implementation
- src/process_threads.py: Process + Threads implementation
- src/rpc_worker.py: RPC worker server (xmlrpc)
- src/rpc_master.py: RPC master client/driver
- data/: Sample text files
- scripts/: Convenience scripts to run demos

Quick Start

Create and activate a virtual environment (optional), then install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Prepare sample data (already included under data/). You can add more .txt files.

Run: Process only

```
bash scripts/run_process_only.sh
```

Run: Process + Threads

```
bash scripts/run_process_threads.sh
```

Run: RPC (Master/Worker)

Terminal 1–3: start 3 workers on ports 9001, 9002, 9003

```
python src/rpc_worker.py --port 9001
python src/rpc_worker.py --port 9002
python src/rpc_worker.py --port 9003
```

Then run master in another terminal:

```
bash scripts/run_rpc.sh
```

Evaluation Notes

- Process only: Simple and robust; good CPU utilization on a single host; overhead due to inter-process communication and data serialization
- Process + Threads: Better for mixed I/O + CPU workloads; threads can hide I/O latency and reduce process creation overhead; Python GIL limits CPU-bound thread speedups within a single process; hybrid model still scales across processes
- RPC: Scales beyond a single machine; adds network latency and serialization overhead; requires service management (start/stop, health, retries)

You can modify number of workers, chunk sizes, and file sets to empirically compare throughput and latency across the three variants.

How to Evaluate (Suggested)

- Dataset sizes: duplicate files under `data/` to create small (~1MB), medium (~50MB), large (~200MB) inputs
- Metrics: measure wall-clock runtime (e.g., `time bash scripts/run_*.sh`) and throughput (total bytes processed / runtime)
- Variables:
  - Process-only: vary `--workers`
  - Process+Threads: vary `--proc-workers` and `--thread-workers`
  - RPC: vary number of workers and simulate remote hosts by starting workers on other machines/containers
- Expectations:
  - Process-only scales with cores up to IPC/merge overhead
  - Process+Threads may outperform when I/O bound; limited by GIL for CPU-only
  - RPC scales across hosts but adds serialization/network overhead; best for multi-node

# distributed_word_count_system
