# -*- coding: utf-8 -*-
import logging
import os
from logging.config import dictConfig
from typing import Iterator, List

from vast import parser
from vast.media import Media
from vast.provider import ResourceProvider

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "vast": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
            "vast.provider": {"handlers": ["default"], "level": "INFO"},
            "canvasapi": {"handlers": ["default"], "level": "WARNING"},
        },
    }
)

logger = logging.getLogger(__name__)


class VastConfig:
    def __init__(self, **kwargs) -> None:
        try:
            self.canvas_api_url = kwargs["canvas_api_url"]
            self.canvas_api_key = kwargs["canvas_api_key"]
            self.course_id = kwargs["course_id"]
            self.exclude = kwargs["exclude"]
            self.youtube_api_key = kwargs["youtube_api_key"]
            self.vimeo_access_token = kwargs["vimeo_access_token"]
        except KeyError:
            logger.exception("Config validation failed")
            raise RuntimeError("Invalid configuration provided to VAST")

    @classmethod
    def from_env(cls, **kwargs) -> "VastConfig":
        config = {
            "canvas_api_url": kwargs.get("canvas_api_url")
            or os.environ.get("CANVAS_API_URL"),
            "canvas_api_key": kwargs.get("canvas_api_key")
            or os.environ.get("CANVAS_API_KEY"),
            "course_id": kwargs.get("course_id") or os.environ.get("COURSE_ID"),
            "exclude": kwargs.get("exclude", []) or os.environ.get("EXCLUDE", []),
            "youtube_api_key": kwargs.get("youtube_api_key")
            or os.environ.get("YOUTUBE_API_KEY"),
            "vimeo_access_token": kwargs.get("vimeo_access_token")
            or os.environ.get("VIMEO_ACCESS_TOKEN"),
        }
        return VastConfig(**config)


class Vast:
    def __init__(self, config) -> None:
        if not config:
            logger.exception("Empty configuration file supplied")
            raise RuntimeError("Invalid configuration provided to VAST")

        self.config = config

    def scan(self) -> List[Media]:
        scanned = []
        for discovered_media in self._get_provider_media():
            for media in discovered_media:
                logger.info(media.type)
                scanned.append(parser.get_metadata(media))
        return scanned

    def _get_provider_media(self) -> Iterator[List[Media]]:
        for provider in self._get_enabled_providers():
            media: List = []
            logger.info("Scanning %s", provider.name)
            content = provider.fetch()
            for item in content:
                media.extend(parser.parse_content(item))
            logger.info("Found %d items", len(media))
            yield media

    def _get_enabled_providers(self) -> Iterator[ResourceProvider]:
        providers = ResourceProvider.__subclasses__()
        for provider in providers:
            if provider.name not in self.config.exclude:
                yield provider(self.config)
            else:
                logger.info("Skipping disabled provider: %s", provider.name)
