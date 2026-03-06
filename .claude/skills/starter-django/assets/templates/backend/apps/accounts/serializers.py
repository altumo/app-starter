from rest_framework import serializers


class UserMeSerializer(serializers.Serializer):
    clerk_id = serializers.CharField()
    session_id = serializers.CharField()
    org_id = serializers.CharField(allow_null=True)
    org_role = serializers.CharField(allow_null=True)
