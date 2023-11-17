import requests
from . import WIX_API_KEY, WIX_SITE_ID


class WixService:
    api_key: str = WIX_API_KEY
    site_id: str = WIX_SITE_ID

    @classmethod
    def get_blog_posts(cls, paging_limit, paging_offset) -> requests.Response:

        headers = {
            'Content-Type': 'application/json',
            'Authorization': cls.api_key,
            'wix-site-id': cls.site_id
        }

        params = {
            'paging.limit': paging_limit,
            'paging.offset': paging_offset
        }

        response = requests.get('http://www.wixapis.com/blog/v3/posts', params=params, headers=headers)

        return response

    @classmethod
    def get_total_posts(cls):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': cls.api_key,
            'wix-site-id': cls.site_id
        }

        response = requests.get('http://www.wixapis.com/blog/v2/stats/posts/total', headers=headers)
        return response

    @classmethod
    def get_post(cls, slug: str):

        headers = {
            'Content-Type': 'application/json',
            'Authorization': cls.api_key,
            'wix-site-id': cls.site_id
        }

        params = {
            'fieldsets': ['CONTENT_TEXT', 'RICH_CONTENT']
        }

        response = requests.get(f'http://www.wixapis.com/blog/v3/posts/slugs/{slug}',
                                params=params, headers=headers)
        return response

    @classmethod
    def get_member(cls, member_id: str):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': cls.api_key,
            'wix-site-id': cls.site_id
        }

        params = {
            'fieldsets': ['FULL']
        }

        response = requests.get(f'https://www.wixapis.com/members/v1/members/{member_id}',
                                params=params, headers=headers)
        return response
