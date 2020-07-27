import argparse
import logging
import pathlib
from dataclasses import dataclass
from typing import Optional, List

import configargparse

BASE_DIR = pathlib.Path(__file__).parent

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('jaundice-rate')
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('pymorphy2').setLevel(logging.WARNING)

@dataclass()
class Config:
    """Project settings."""
    port: int = 8080
    request_timeout: float = 2.0
    process_timeout: float = 3.0
    urls_limit: int = 10

def _create_parser() -> argparse.ArgumentParser:
    """Creates a parser to process command line arguments."""
    parser = configargparse.ArgParser(description='News detector')
    parser.add_argument(
        '--port',
        type=int,
        help='Port for listening',
        default=Config.port,
        env_var='NEWS_PORT',
    )
    parser.add_argument(
        '--request_timeout',
        type=float,
        help='Timeout for downloading a page from remote server',
        default=Config.request_timeout,
        env_var='NEWS_REQUEST_TIMEOUT',
    )
    parser.add_argument(
        '--process_timeout',
        type=float,
        help='Timeout for processing page content',
        default=Config.process_timeout,
        env_var='NEWS_PROCESS_TIMEOUT',
    )
    parser.add_argument(
        '--urls_limit',
        type=int,
        help='Max number of urls in a batch',
        default=Config.urls_limit,
        env_var='NEWS_URL_LIMIT',
    )
    return parser

def load_settings(cmd_params: Optional[List[str]] = None) -> Config:
    """Read settings from env variables and command-line arguments."""
    parser = _create_parser()
    settings = parser.parse_args(args=cmd_params)
    return Config(
        port=settings.port,
        request_timeout=settings.request_timeout,
        process_timeout=settings.process_timeout,
        urls_limit=settings.urls_limit,
    )
