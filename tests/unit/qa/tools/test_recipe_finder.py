import pytest
import json
from app.services.qa.tools.recipe_finder import recipe_finder_tool


def test_null_recipe():
    query: str = "AErgrgrs"
    result: str = recipe_finder_tool._run(query)
    result: dict = json.loads(result)
    assert len(result) == 0
    assert result == {}
    assert result == {}


def test_recipe():
    query: str = "German Wheat Beer"
    result: str = recipe_finder_tool._run(query)
    result: dict = json.loads(result)
    assert len(result) > 0
    assert len(result["recipes"]) == 1
