# plagiarism_backend/checker/serializers.py
from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    text = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get("file") and not data.get("text"):
            raise serializers.ValidationError("Provide either 'text' or 'file'.")
        return data
