import argparse
from typing import Dict, List, Tuple
from xmlrpc.client import ServerProxy
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils import list_text_files, chunk_files, merge_counts, format_top_n


def dispatch_round_robin(workers: List[ServerProxy], chunks: List[Tuple[str, str]]) -> Dict[str, int]:
	result: Dict[str, int] = {}
	if not workers or not chunks:
		return result
	# Submit RPC calls concurrently
	futures = []
	with ThreadPoolExecutor(max_workers=len(workers)) as ex:
		for idx, (_, text) in enumerate(chunks):
			w = workers[idx % len(workers)]
			futures.append(ex.submit(w.map_chunk, text))
		for fut in as_completed(futures):
			partial = fut.result()
			merge_counts(result, partial)
	return result


def run(data_dir: str, worker_urls: List[str], top_n: int) -> Dict[str, int]:
	workers = [ServerProxy(url, allow_none=True) for url in worker_urls]
	# Optional health checks
	for w in workers:
		try:
			_ = w.health()
		except Exception as e:
			raise RuntimeError(f"Worker unhealthy/unreachable: {w}") from e
	paths = list_text_files(data_dir)
	chunks = chunk_files(paths)
	return dispatch_round_robin(workers, chunks)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--data", required=True)
	parser.add_argument("--workers", nargs='+', required=True, help="List of worker URLs, e.g. http://localhost:9001")
	parser.add_argument("--top", type=int, default=20)
	args = parser.parse_args()
	res = run(args.data, args.workers, args.top)
	print(format_top_n(res, args.top))


if __name__ == "__main__":
	main()


