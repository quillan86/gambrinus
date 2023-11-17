import requests
from . import CLOSE_API_KEY


class CloseService:
    api_key: str = CLOSE_API_KEY


    @classmethod
    def search_lead_by_email(cls, email: str) -> list:
        query = {
            "limit": None,
            "query": {
                "negate": False,
                "queries": [
                    {
                        "negate": False,
                        "object_type": "lead",
                        "type": "object_type"
                    },
                    {
                        "negate": False,
                        "queries": [
                            {
                                "negate": False,
                                "related_object_type": "contact",
                                "related_query": {
                                    "negate": False,
                                    "queries": [
                                        {
                                            "negate": False,
                                            "related_object_type": "contact_email",
                                            "related_query": {
                                                "negate": False,
                                                "queries": [
                                                    {
                                                        "condition": {
                                                            "mode": "full_words",
                                                            "type": "text",
                                                            "value": email
                                                        },
                                                        "field": {
                                                            "field_name": "email",
                                                            "object_type": "contact_email",
                                                            "type": "regular_field"
                                                        },
                                                        "negate": False,
                                                        "type": "field_condition"
                                                    }
                                                ],
                                                "type": "and"
                                            },
                                            "this_object_type": "contact",
                                            "type": "has_related"
                                        }
                                    ],
                                    "type": "and"
                                },
                                "this_object_type": "lead",
                                "type": "has_related"
                            }
                        ],
                        "type": "and"
                    }
                ],
                "type": "and"
            },
            "results_limit": None,
            "sort": []
        }

        try:
            response = requests.post('https://api.close.com/api/v1/data/search/', json=query, auth=(cls.api_key, ''))
            result = [x.get('id') for x in response.json()]
            return result
        except Exception:
            return []

    @classmethod
    def create_lead(cls, email: str):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        json_data = {
            "name": email,
            "website": email.split('@')[1],
            "contacts": [
                {
                    "name": email,
                    "emails": [

                        {
                            'email': email,
                            'type': 'office',
                        },
                    ]
                }
            ],
            "custom.cf_iyN6hcPhuC49ViehbzE6U9EKGyfFKy9oiSBOagDZJmt": "User"
        }
        try:
            response = requests.post('https://api.close.com/api/v1/lead/', headers=headers, json=json_data,
                                     auth=(cls.api_key, ''))
            # check
            return response.json().get('custom.cf_iyN6hcPhuC49ViehbzE6U9EKGyfFKy9oiSBOagDZJmt') == 'User'
        except Exception:
            return False
