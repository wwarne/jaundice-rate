import logging
import pathlib


BASE_DIR = pathlib.Path(__file__).parent

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('jaundice-rate')
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('pymorphy2').setLevel(logging.WARNING)
