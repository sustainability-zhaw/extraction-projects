import logging
import settings

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger("extractor_project")
