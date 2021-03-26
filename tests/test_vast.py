# -*- coding: utf-8 -*-
import pytest

from vast.vast import Vast, VastConfig


class TestVastConfig:
    @pytest.mark.skip
    def test_vast_initializes_with_valid_config(self):
        config = VastConfig()
        assert Vast(config=config) is not None

    def test_vastconfig_throws_runtime_error_with_missing_keys(self):
        with pytest.raises(RuntimeError):
            config = VastConfig()

    def test_vast_throws_runtime_error_without_config(self):
        with pytest.raises(RuntimeError):
            Vast(config=None)


class TestVast:
    @pytest.mark.vcr()
    def test_scan_produces_processed_media_items(self, vast):
        scanned = vast.scan()
        assert scanned is not None
        import ipdb

        ipdb.set_trace()
