from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ...services.security import api_key_auth
from ...services.integration.wix import WixService
from fastapi.security.api_key import APIKey
from enum import Enum
import requests
import traceback


router = APIRouter(
    prefix="/blog",
    tags=["website"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_posts(paging_limit: int = 4, paging_offset: int = 1, api_key: APIKey = Depends(api_key_auth)) -> list[dict]:
    """
    Get an array of Wix blog posts. Check https://dev.wix.com/docs/rest/api-reference/wix-blog/blog/posts-stats/list-posts
    for more details.

    - Args:
        - **paging_limit** (int): How many blog posts to return at maximum in the resonse.
        - **paging_offset** (int): Offset of the blog posts.

    - Returns:
        - **list[dict]**: List of blog posts

    - Raise:
        - **HTTPException**: If there is an error in the wix response.
    """

    response = WixService.get_blog_posts(paging_limit, paging_offset)

    if response.status_code == 200:
        result = response.json()['posts']

        for i, post in enumerate(result):
            post["offset"] = paging_offset + i


        return result
    else:
        raise HTTPException(status_code=response.status_code)


@router.get("/{slug}/", status_code=status.HTTP_200_OK)
async def get_post(slug: str, api_key: APIKey = Depends(api_key_auth)) -> dict:
    """
    Get a specific Wix blog post. Check https://dev.wix.com/docs/rest/api-reference/wix-blog/blog/posts-stats/get-post
    for more details.
    The plain text is stored in contentText, rich text is stored in richContent.

    - Args:
        - **post_id** (str): ID of the blog post (typically a UUID)

    - Returns:
        - **dict**: A blog post

    - Raise:
        - **HTTPException**: If there is an error in the wix response.
    """
    response = WixService.get_post(slug)

    if response.status_code == 200:
        result = response.json()['post']
        return result
    else:
        raise HTTPException(status_code=response.status_code)


@router.get("/total", status_code=status.HTTP_200_OK)
async def get_total_posts(api_key: APIKey = Depends(api_key_auth)) -> int:
    """
    Get the total number of blog posts.

    - Returns:
        - **int**: Number of blog posts.
    """
    response = WixService.get_total_posts()
    if response.status_code == 200:
        result = response.json()['total']
        return result
    else:
        raise HTTPException(status_code=response.status_code)


@router.get("/member/{member_id}/", status_code=status.HTTP_200_OK)
async def get_member(member_id: str, api_key: APIKey = Depends(api_key_auth)) -> dict:
    """
    Get a specific Wix member. Check https://dev.wix.com/docs/rest/api-reference/members/members/get-member
    for more details.

    - Args:
        - **post_id** (str): ID of the blog post (typically a UUID)

    - Returns:
        - **dict**: A blog post

    - Raise:
        - **HTTPException**: If there is an error in the wix response.
    """
    response = WixService.get_member(member_id)

    if response.status_code == 200:
        result = response.json()['member']
        return result
    else:
        raise HTTPException(status_code=response.status_code)
