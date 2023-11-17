from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security.api_key import APIKey
from typing import Union, Optional
from ...services.security import api_key_auth
from ...services.qa.tools import beer_qa_tool, recipe_finder_tool, flavor_profiler_tool, wikipedia_tool, pubmed_tool
import json
from enum import Enum

router = APIRouter(
    prefix="/tool",
    tags=["assistant"]
)


class BeerType(str, Enum):
    beer_style = "beer_style"
    beer_recipe = "beer_recipe"
    beer_ingredient = "beer_ingredient"


class BeerTypeMod(str, Enum):
    beer_style = "beer_style"
    beer_recipe = "beer_recipe"


class FlavorProfilerMethod(str, Enum):
    identify_flavor = "identify_flavor"
    adjust_recipe = "adjust_recipe"
    substitute_ingredient = "substitute_ingredient"
    add_ingredient = "add_ingredient"
    remove_ingredient = "remove_ingredient"


@router.get("/beer_knowledge/", status_code=status.HTTP_200_OK)
async def beer_knowledge(question: str, api_key: APIKey = Depends(api_key_auth)) -> dict[str, Union[str, list[str]]]:
    """

    :param question: Question to query the knowledge base.
    :return:
    """
    result = json.loads(beer_qa_tool._run(question))
    return result


@router.get("/recipe_finder/", status_code=status.HTTP_200_OK)
async def recipe_finder(query: str, type: BeerType, api_key: APIKey = Depends(api_key_auth)):
    """

    :param query: Recipe to query.
    :param type: Type (beer_style, beer_recipe,
    :return:
    """
    result = json.loads(recipe_finder_tool._run(query, type.value))
    return result


@router.get("/flavor_profiler/", status_code=status.HTTP_200_OK)
async def flavor_profiler(query: str, type: BeerTypeMod, method: FlavorProfilerMethod, ingredient: Optional[str] = None, api_key: APIKey = Depends(api_key_auth)):
    """

    :param query: Recipe to query.
    :return:
    """
    result = json.loads(flavor_profiler_tool._run(query, type.value, method.value, ingredient))
    return result


@router.get("/wikipedia/", status_code=status.HTTP_200_OK)
async def wikipedia(question: str):
    """

    :param query: Search Query for Wikipedia.
    :return:
    """
    result = json.loads(wikipedia_tool._run(question))
    return result


@router.get("/pubmed/", status_code=status.HTTP_200_OK)
async def pubmed(question: str):
    """

    :param query: Search Query for PubMed.
    :return:
    """
    result = json.loads(pubmed_tool._run(question))
    return result
