import importlib

import pytest

LAYERS = ["core", "adapters", "ingestion", "catalog", "web", "cli"]


def test_package_imports():
    assert importlib.import_module("fit_my_ride")


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_imports(layer):
    assert importlib.import_module(f"fit_my_ride.{layer}")
