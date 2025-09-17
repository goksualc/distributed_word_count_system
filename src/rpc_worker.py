import argparse
from xmlrpc.server import SimpleXMLRPCServer
from typing import Dict
import os, sys
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)
from src.utils import count_words


class WordCountService:
	def health(self) -> str:
		return "ok"

	def map_chunk(self, text: str) -> Dict[str, int]:
		return count_words(text)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="0.0.0.0")
	parser.add_argument("--port", type=int, required=True)
	args = parser.parse_args()
	server = SimpleXMLRPCServer((args.host, args.port), allow_none=True, logRequests=False)
	service = WordCountService()
	server.register_instance(service)
	print(f"RPC worker listening on {args.host}:{args.port}")
	server.serve_forever()


if __name__ == "__main__":
	main()


