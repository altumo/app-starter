from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class MeView(APIView):
    """Return the current authenticated user's information from Clerk JWT."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        clerk_user = request.user
        return Response(
            {
                "clerk_id": clerk_user.clerk_id,
                "session_id": clerk_user.session_id,
                "org_id": clerk_user.org_id,
                "org_role": clerk_user.org_role,
            }
        )
