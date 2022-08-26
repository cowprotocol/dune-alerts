"""
Factory method to load QueryMonitor object from yaml configuration files
"""
from __future__ import annotations

import yaml
from duneapi.types import QueryParameter

from src.models import TimeWindow, LeftBound
from src.query_monitor.base import QueryBase, QueryData
from src.query_monitor.counter import CounterQueryMonitor
from src.query_monitor.left_bounded import LeftBoundedQueryMonitor
from src.query_monitor.result_threshold import ResultThresholdQuery
from src.query_monitor.windowed import WindowedQueryMonitor


def load_from_config(config_yaml: str) -> QueryBase:
    """Loads a QueryMonitor object from yaml configuration file"""
    with open(config_yaml, "r", encoding="utf-8") as yaml_file:
        cfg = yaml.load(yaml_file, yaml.Loader)

    query = QueryData(
        name=cfg["name"],
        query_id=cfg["id"],
        params=[
            QueryParameter.from_dict(param_cfg)
            for param_cfg in cfg.get("parameters", [])
        ],
    )

    threshold = cfg.get("threshold", 0)
    if "window" in cfg:
        # Windowed Query
        window = TimeWindow.from_cfg(cfg["window"])
        return WindowedQueryMonitor(query, window, threshold)
    if "left_bound" in cfg:
        # Left Bounded Query
        left_bound = LeftBound.from_cfg(cfg["left_bound"])
        return LeftBoundedQueryMonitor(query, left_bound, threshold)

    if "column" in cfg and "alert_value" in cfg:
        # Counter Query
        column, alert_value = cfg["column"], float(cfg["alert_value"])
        return CounterQueryMonitor(query, column, alert_value)

    return ResultThresholdQuery(query, threshold)
