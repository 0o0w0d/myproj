from rest_framework import serializers
from .models import Post, Comment
from accounts.models import User
from django.db.models import QuerySet

# serializers -> forms과 유사


class AuthorSerializer(serializers.ModelSerializer):
    # default로 self.get_{field} 메서드를 자동 호출
    name = serializers.SerializerMethodField()

    def get_name(self, user) -> str:
        return f"{user.last_name} {user.first_name}".strip()

    class Meta:
        model = User
        fields = ["id", "username", "email", "name"]


class CommentSerializier(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "message"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content"]

    @staticmethod
    def get_optimized_queryset() -> QuerySet[Post]:
        return Post.objects.all()


class PostListSerializer(serializers.ModelSerializer):
    # Model에서 __str__ 속성으로 지정된 값 반환
    # AbstractUser default config : __str__ -> 'username'
    # author = serializers.StringRelatedField()
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = ["id", "title", "author"]

    @staticmethod
    def get_optimized_queryset() -> QuerySet[Post]:
        return Post.objects.all().only("id", "title", "author").select_related("author")


class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    # comment_list = serializers.StringRelatedField(source="comment_set", many=True)
    # 역참조 관계이기 때문에 source 속성 지정 필수 (Post 인스턴스에 comment 값이 없고, author 값은 있음)
    comment_list = CommentSerializier(source="comment_set", many=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "author", "comment_list"]

    @staticmethod
    def get_optimized_queryset() -> QuerySet[Post]:
        return Post.objects.all()
