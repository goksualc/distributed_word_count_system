import os
import re
import math
from typing import Dict, Iterable, List, Tuple


WORD_RE = re.compile(r"[A-Za-z]+")


def read_file(path: str) -> str:
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return f.read()


def tokenize(text: str) -> List[str]:
	return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def count_words(text: str) -> Dict[str, int]:
	counts: Dict[str, int] = {}
	for w in tokenize(text):
		counts[w] = counts.get(w, 0) + 1
	return counts


def merge_counts(a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
	for w, c in b.items():
		a[w] = a.get(w, 0) + c
	return a


def list_text_files(directory: str) -> List[str]:
	paths: List[str] = []
	for name in os.listdir(directory):
		if name.lower().endswith(".txt"):
			paths.append(os.path.join(directory, name))
	return sorted(paths)


def chunk_text(text: str, target_chunk_size: int = 200_000) -> List[str]:
	# Split text into near-equal chunks without splitting words badly; fall back to naive slicing
	if len(text) <= target_chunk_size:
		return [text]
	chunks: List[str] = []
	start = 0
	while start < len(text):
		end = min(len(text), start + target_chunk_size)
		# try to extend to next whitespace to avoid splitting a word
		while end < len(text) and text[end].isalpha():
			end += 1
		chunks.append(text[start:end])
		start = end
	return chunks


def chunk_files(paths: List[str], target_chunk_size: int = 200_000) -> List[Tuple[str, str]]:
	# Returns list of (origin_path, text_chunk)
	result: List[Tuple[str, str]] = []
	for p in paths:
		text = read_file(p)
		for ch in chunk_text(text, target_chunk_size):
			result.append((p, ch))
	return result


def format_top_n(counts: Dict[str, int], top_n: int = 20) -> str:
	items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
	lines = [f"{w}\t{c}" for w, c in items]
	return "\n".join(lines)


