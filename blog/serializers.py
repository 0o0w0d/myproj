from rest_framework import serializers
from .models import Post

# serializers -> forms과 유사


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content"]
