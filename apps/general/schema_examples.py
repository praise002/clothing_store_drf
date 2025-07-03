from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)


from apps.common.schema_examples import (
    AVATAR_URL,
    DATETIME_EXAMPLE,
    EMAIL_EXAMPLE,
    SUCCESS_RESPONSE_STATUS,
)
from apps.common.serializers import ErrorDataResponseSerializer
from apps.general.serializers import (
    MessageSerializer,
    SiteDetailSerializer,
    TeamMemberSerializer,
)


SITE_DETAIL_EXAMPLE = {
    "name": "Clothing Store",
    "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "phone": "+23412345678",
    "address": "23, Lagos, Nigeria",
    "email": "company@example.com",
    "company_socials": {
        "id": 1,
        "fb": "https://facebook.com",
        "tw": "https://x.com",
        "ln": "https://linkedin.com",
        "ig": "https://instagram.com",
        "name": "Site detail socials",
    },
}

TEAM_MEMBER_EXAMPLE = [
    {
        "name": "Femi Otedola",
        "role": "CO-Founder",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "avatar_url": AVATAR_URL,
        "social_links": {
            "id": 2,
            "fb": "https://facebook.com",
            "tw": "https://x.com",
            "ln": "https://linkedin.com",
            "ig": "https://instagram.com",
            "name": "Team Member 1 socials",
        },
    },
    {
        "name": "Johnny Drille",
        "role": "Product Expert",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "avatar_url": AVATAR_URL,
        "social_links": {
            "id": 3,
            "fb": "https://facebook.com",
            "tw": "https://x.com",
            "ln": "https://linkedin.com",
            "ig": "https://instagram.com",
            "name": "Team Member 2 socials",
        },
    },
    {
        "name": "Hilda Baci",
        "role": "General Manager",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "avatar_url": AVATAR_URL,
        "social_links": {
            "id": 4,
            "fb": "https://facebook.com",
            "tw": "https://x.com",
            "ln": "https://linkedin.com",
            "ig": "https://instagram.com",
            "name": "Team Member 3 socials",
        },
    },
]

# MESSAGE_CREATE_EXAMPLE = {
#     "name": "Bobby Johnson",
#     "email": EMAIL_EXAMPLE,
#     "subject": "Test subject",
#     "text": "Test text",
#     "sent_at": DATETIME_EXAMPLE,
# }

SITE_DETAIL_RESPONSE_EXAMPLE = {
    #     200: SiteDetailResponseSerializer,
    200: OpenApiResponse(
        response=SiteDetailSerializer,
        description="Site Detail Retrieval Successful",
        examples=[
            OpenApiExample(
                name="Site Detail Retrieval Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Site detail retrieved successfully.",
                    "data": SITE_DETAIL_EXAMPLE,
                },
            ),
        ],
    ),
}

TEAM_MEMBER_RESPONSE_EXAMPLE = {
    #     200: TeamMemberResponseSerializer,
    200: OpenApiResponse(
        response=TeamMemberSerializer,
        description="Team Members Retrieval Successful",
        examples=[
            OpenApiExample(
                name="Team Members Retrieval Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Team members retrieved successfullyy.",
                    "data": TEAM_MEMBER_EXAMPLE,
                },
            ),
        ],
    ),
}

MESSAGE_RESPONSE_EXAMPLE = {
    #     201: MessageResponseSerializer,
    #     422: ErrorDataResponseSerializer,
    201: OpenApiResponse(
        response=MessageSerializer,
        description="Message Sent Successful",
        examples=[
            OpenApiExample(
                name="Message Sent Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Message sent successfully.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}
