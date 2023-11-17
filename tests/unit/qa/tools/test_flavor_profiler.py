import pytest
import json
from app.services.qa.tools.flavor_profiler import flavor_profiler_tool


def test_null_recipe():
    query: str = "AErgrgrs"
    result: str = flavor_profiler_tool._run(query)
    result: dict = json.loads(result)
    assert len(result['unnormalized_flavor_profile']) == 0
    assert len(result['normalized_flavor_profile']) == 0


def test_recipe():
    query: str = "German Wheat Beer"
    result: str = flavor_profiler_tool._run(query)
    result: dict = json.loads(result)
    for flavor_type in ['taste', 'odor', 'texture']:
        normalized_flavor_sum = sum([x for x in result['normalized_flavor_profile'][flavor_type].values()])
        assert normalized_flavor_sum == 100
    assert len(result['unnormalized_flavor_profile']) > 0
    assert len(result['normalized_flavor_profile']) > 0
