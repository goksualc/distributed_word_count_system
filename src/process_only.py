import argparse
import multiprocessing as mp
from typing import Dict, List, Tuple

from src.utils import count_words, merge_counts, list_text_files, chunk_files, format_top_n


def _map_chunk(args: Tuple[str, str]) -> Dict[str, int]:
	# args: (origin_path, text_chunk)
	_, chunk = args
	return count_words(chunk)


def run(data_dir: str, workers: int, top_n: int) -> Dict[str, int]:
	paths = list_text_files(data_dir)
	chunks = chunk_files(paths)
	with mp.Pool(processes=workers) as pool:
		partials = pool.map(_map_chunk, chunks)
	result: Dict[str, int] = {}
	for p in partials:
		merge_counts(result, p)
	return result


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--data", required=True, help="Directory with .txt files")
	parser.add_argument("--workers", type=int, default=4)
	parser.add_argument("--top", type=int, default=20)
	args = parser.parse_args()
	res = run(args.data, args.workers, args.top)
	print(format_top_n(res, args.top))


if __name__ == "__main__":
	main()


