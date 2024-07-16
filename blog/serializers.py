from rest_framework import serializers
from .models import Post
from accounts.models import User

# serializers -> forms과 유사


class AuthorSerializer(serializers.ModelSerializer):
    # default로 self.get_{field} 메서드를 자동 호출
    name = serializers.SerializerMethodField()

    def get_name(self, user) -> str:
        return f"{user.last_name} {user.first_name}".strip()

    class Meta:
        model = User
        fields = ["id", "username", "email", "name"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content"]


class PostListSerializer(serializers.ModelSerializer):
    # Model에서 __str__ 속성으로 지정된 값 반환
    # AbstractUser default config : __str__ -> 'username'
    # author = serializers.StringRelatedField()
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = ["id", "title", "author"]


class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = ["id", "title", "content", "author"]
