from rest_framework import serializers
from .models import Post

# serializers -> forms과 유사


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content"]


class PostListSerializer(serializers.ModelSerializer):
    # Model에서 __str__ 속성으로 지정된 값 반환
    # AbstractUser default config : __str__ -> 'username'
    # author = serializers.StringRelatedField()
    author = serializers.CharField(source="author.username")

    class Meta:
        model = Post
        fields = ["id", "title", "author"]


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username")

    class Meta:
        model = Post
        fields = ["id", "title", "content", "author"]
