import argparse
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple
import os, sys
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)
from src.utils import count_words, merge_counts, list_text_files, chunk_files, format_top_n


def _thread_map(chunks: List[Tuple[str, str]], thread_workers: int) -> Dict[str, int]:
	result: Dict[str, int] = {}
	with ThreadPoolExecutor(max_workers=thread_workers) as ex:
		for partial in ex.map(lambda arg: count_words(arg[1]), chunks):
			merge_counts(result, partial)
	return result


def _proc_worker(args: Tuple[List[Tuple[str, str]], int]) -> Dict[str, int]:
	chunks, thread_workers = args
	return _thread_map(chunks, thread_workers)


def run(data_dir: str, proc_workers: int, thread_workers: int, top_n: int) -> Dict[str, int]:
	paths = list_text_files(data_dir)
	all_chunks = chunk_files(paths)
	if not all_chunks:
		return {}
	# Split chunks among processes
	per_proc = max(1, (len(all_chunks) + proc_workers - 1) // proc_workers)
	proc_args: List[Tuple[List[Tuple[str, str]], int]] = []
	for i in range(0, len(all_chunks), per_proc):
		proc_args.append((all_chunks[i:i+per_proc], thread_workers))
	with mp.Pool(processes=proc_workers) as pool:
		partials = pool.map(_proc_worker, proc_args)
	result: Dict[str, int] = {}
	for p in partials:
		merge_counts(result, p)
	return result


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--data", required=True)
	parser.add_argument("--proc-workers", type=int, default=3)
	parser.add_argument("--thread-workers", type=int, default=4)
	parser.add_argument("--top", type=int, default=20)
	args = parser.parse_args()
	res = run(args.data, args.proc_workers, args.thread_workers, args.top)
	print(format_top_n(res, args.top))


if __name__ == "__main__":
	main()


