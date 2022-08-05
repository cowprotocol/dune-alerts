"""
Instead of multiple importing log statements and defining a preconfigured log in every file,
this completes the job over two line as follows:

```
from src.logging import set_log

log = set_log(__name__)
```
"""
import logging.config
from logging import Logger


def set_log(name: str) -> Logger:
    """Sets and returns log with given `name` preconfigured from project's root"""
    log = logging.getLogger(name)
    logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
    return log
