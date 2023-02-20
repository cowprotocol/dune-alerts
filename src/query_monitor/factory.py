"""
Factory method to load QueryMonitor object from yaml configuration files
"""
from __future__ import annotations
import os
from dataclasses import dataclass

import logging.config
import yaml
from dune_client.types import QueryParameter
from dune_client.query import Query

from src.models import TimeWindow, LeftBound
from src.query_monitor.base import QueryBase
from src.query_monitor.counter import CounterQueryMonitor
from src.query_monitor.left_bounded import LeftBoundedQueryMonitor
from src.query_monitor.result_threshold import ResultThresholdQuery
from src.query_monitor.windowed import WindowedQueryMonitor


log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


@dataclass
class Config:
    """
    Model for content contained in query config.yaml file
    """

    query: QueryBase
    ping_frequency: int
    alert_channel: str


def load_config(config_yaml: str) -> Config:
    """Loads a QueryMonitor object from yaml configuration file"""
    with open(config_yaml, "r", encoding="utf-8") as yaml_file:
        cfg = yaml.load(yaml_file, yaml.Loader)
    log.debug(f"config {config_yaml} loaded as {cfg}")
    query = Query(
        name=cfg["name"],
        query_id=cfg["id"],
        params=[
            QueryParameter.from_dict(param_cfg)
            for param_cfg in cfg.get("parameters", [])
        ],
    )

    threshold = cfg.get("threshold", 0)
    base_query: QueryBase
    if "window" in cfg:
        # Windowed Query
        window = TimeWindow.from_cfg(cfg["window"])
        base_query = WindowedQueryMonitor(query, window, threshold)
    elif "left_bound" in cfg:
        # Left Bounded Query
        left_bound = LeftBound.from_cfg(cfg["left_bound"])
        base_query = LeftBoundedQueryMonitor(query, left_bound, threshold)
    elif "column" in cfg and "alert_value" in cfg:
        # Counter Query
        column, alert_value = cfg["column"], float(cfg["alert_value"])
        base_query = CounterQueryMonitor(query, column, alert_value)
    else:
        base_query = ResultThresholdQuery(query, threshold)

    config_obj = Config(
        query=base_query,
        # Use specified channel, or default to "global config"
        alert_channel=cfg.get("alert_channel", os.environ["SLACK_ALERT_CHANNEL"]),
        # This is 4x the DuneClient default of 5 seconds
        ping_frequency=cfg.get("ping_frequency", 20),
    )
    log.debug(f"config parsed as {config_obj}")
    return config_obj
