"""
Factory method to load QueryMonitor object from yaml configuration files
"""
from __future__ import annotations

import yaml
from duneapi.types import QueryParameter

from src.models import TimeWindow, LeftBound
from src.query_monitor.base import BaseQueryMonitor, QueryMonitor
from src.query_monitor.left_bounded import LeftBoundedQueryMonitor
from src.query_monitor.windowed import WindowedQueryMonitor


def load_from_config(config_yaml: str) -> BaseQueryMonitor:
    """Loads a QueryMonitor object from yaml configuration file"""
    with open(config_yaml, "r", encoding="utf-8") as yaml_file:
        cfg = yaml.load(yaml_file, yaml.Loader)

    name, query_id = cfg["name"], cfg["id"]
    threshold = cfg.get("threshold", 0)
    params = [
        QueryParameter.from_dict(param_cfg) for param_cfg in cfg.get("parameters", [])
    ]
    if "window" in cfg:
        # Windowed Query
        window = TimeWindow.from_cfg(cfg["window"])
        return WindowedQueryMonitor(name, query_id, window, params, threshold)
    if "left_bound" in cfg:
        # Left Bounded Query
        left_bound = LeftBound.from_cfg(cfg["left_bound"])
        return LeftBoundedQueryMonitor(name, query_id, left_bound, params, threshold)

    return QueryMonitor(name, query_id, params, threshold)
