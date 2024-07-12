from django.db import models
from django.contrib.auth.models import AbstractUser


# project begging step, add custom User(not use auth.User)
class User(AbstractUser):
    following_set = models.ManyToManyField(
        "self", related_name="follower_set", symmetrical=False, blank=True
    )

    # following 관계에 대한 메서드 추가
    def is_follower(self, to_user) -> bool:
        return self.following_set.filter(pk=to_user.pk).exists()

    def follow(self, to_user) -> None:
        return self.following_set.add(to_user)

    def unfollowing(self, to_user) -> None:
        return self.following_set.remove(to_user)

    # 유저가 팔로우하고 있는 사람
    def follower_count(self) -> int:
        return self.follower_set.count()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True)
