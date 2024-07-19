import base64
import pytest

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory
from blog.models import Post
from blog.tests.factories import PostFactory


def create_user(raw_password: str = None) -> User:
    """
    새로운 User 인스턴스 생성 및 반환
    """
    return UserFactory(raw_password=raw_password)


def get_api_client_with_basic_auth(user: User, raw_password: str) -> APIClient:
    """
    인자의 User 인스턴스와 암호 기반에서 Basic 인증을 적용한 APIClient 인스턴스 반환
    """

    # *.http 파일에서는 자동으로 base64 인코딩을 수행해줬었습니다.
    base64_data: bytes = f"{user.username}:{raw_password}".encode()
    authorization_header: str = base64.b64encode(base64_data).decode()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Basic {authorization_header}")
    return client


@pytest.fixture
def unauthenticated_api_client() -> APIClient:
    """
    Authorization 인증 헤더가 없는 기본 APIClient 인스턴스 반환
    """
    return APIClient()


@pytest.fixture
def api_client_with_new_user_basic_auth(faker) -> APIClient:
    """
    새로운 User 인스턴스 생성 후, 그 User의 인증 정보가 Authorization 인증 헤더로 포함된 APIClient 인스턴스 반환
    """
    raw_password: str = faker.password()
    user: User = create_user(raw_password)
    api_client: APIClient = get_api_client_with_basic_auth(user, raw_password)
    return api_client


@pytest.fixture
def new_user() -> User:
    """
    새로운 User 인스턴스 생성 및 반환
    """
    return create_user()


@pytest.fixture
def new_post() -> Post:
    """
    새로운 Post 인스턴스 반환
    """
    return PostFactory()


@pytest.mark.it(
    "게시물 목록 조회. 비인증 조회가 가능해야하며, 생성한 포스팅의 개수만큼 응답을 받아야 합니다."
)
@pytest.mark.django_db  # pytest DB 접근 허용
def test_post_list(unauthenticated_api_client):
    post_list = [PostFactory() for __ in range(10)]

    url = reverse("blog:api-v1:post_list")
    response: Response = unauthenticated_api_client.get(url)
    assert status.HTTP_200_OK == response.status_code
    assert len(post_list) == len(response.data["result"])


@pytest.mark.it(
    "특정 게시물 조회. 비인증 조회가 가능해야하며, 생성한 포스팅을 조회할 수 있어야 합니다."
)
@pytest.mark.django_db
def test_post_retrieve(unauthenticated_api_client):
    new_post = PostFactory()

    url: str = reverse("blog:api-v1:post_detail", args=[new_post.pk])
    response: Response = unauthenticated_api_client.get(url)
    assert status.HTTP_200_OK == response.status_code
    assert new_post.title == response.data["result"]["title"]


@pytest.mark.it("인증하지 않은 요청은 생성 요청 거부")
@pytest.mark.django_db
def test_unauthenticated_user_cant_create_post(unauthenticated_api_client):
    url = reverse("blog:api-v1:post_new")
    response: Response = unauthenticated_api_client.post(url, data={})
    assert status.HTTP_403_FORBIDDEN == response.status_code


@pytest.mark.it("인증된 요청은 생성 요청 성공")
@pytest.mark.django_db
def test_authenticated_user_can_create_post(api_client_with_new_user_basic_auth, faker):
    url = reverse("blog:api-v1:post_new")
    data = {"title": faker.sentence(), "content": faker.paragraph()}
    response: Response = api_client_with_new_user_basic_auth.post(url, data=data)
    assert status.HTTP_201_CREATED == response.status_code
    assert data["title"] == response.data["title"]
    assert data["content"] == response.data["content"]


# test 함수 안에서 for 문을 통해 값을 test하게 되면, 어느 부분에서 틀렸는지 알 수 없음(하나의 테스트)
# parametrize를 사용하면 여러 개의 테스트 생성 => 어느 부분이 틀렸는지 확인 가능
@pytest.mark.it("필수 필드가 누락된 생성 요청은 거부되어야 합니다.")
@pytest.mark.django_db
@pytest.mark.parametrize("title, content", [("", "content"), ("title", ""), ("", "")])
def test_missing_required_fields_cant_create_post(
    api_client_with_new_user_basic_auth, title, content
):
    url = reverse("blog:api-v1:post_new")
    data = {"title": title, "content": content}
    response: Response = api_client_with_new_user_basic_auth.post(url, data=data)
    assert status.HTTP_400_BAD_REQUEST == response.status_code


"""
수정, 삭제 테스트 idea
    실패 시나리오
    - 임의의 Post를 생성하고, 임의의 유저 인증 정보가 담긴 APIClient 이용
    
    성공 시나리오
    - 유저를 생성하고, 그 유저를 작성자로 Post를 하나 생성 -> 그 Post에 대해서 검사 수행
    - 유저를 따로 생성했으므로, 해당 유저의 인증 정보가 담긴 APIClient 이용(get_api_client_with_basic_auth 함수 사용)
"""


@pytest.mark.it("작성자가 아닌 유저가 수정 요청하면 거부")
@pytest.mark.django_db
def test_non_author_cant_update_post(new_post, api_client_with_new_user_basic_auth):
    url = reverse("blog:api-v1:post_edit", args=[new_post.pk])
    response: Response = api_client_with_new_user_basic_auth.patch(url, data={})
    assert status.HTTP_403_FORBIDDEN == response.status_code


@pytest.mark.it("작성자가 수정 요청하면 성공")
@pytest.mark.django_db
def test_author_can_update_post(faker):
    raw_password = faker.password()
    user = create_user(raw_password=raw_password)
    new_post = PostFactory(author=user)

    url = reverse("blog:api-v1:post_edit", args=[new_post.pk])
    edit_title = faker.sentence()

    apiclient = get_api_client_with_basic_auth(user=user, raw_password=raw_password)
    response: Response = apiclient.patch(url, data={"title": edit_title})
    assert status.HTTP_200_OK == response.status_code
    assert edit_title == response.data["title"]


# 삭제 요청 api를 하나의 클래스로 그룹화 => 테스트 메서드가 인스턴스 메서드로 self 인자를 필요로 함
@pytest.mark.describe("Post 삭제 API test")
class TestPostDeleteGroup:
    @pytest.mark.it("작성자가 아닌 유저가 삭제 요청하면 거부")
    @pytest.mark.django_db
    def test_non_author_cant_delete_post(
        self, new_post, api_client_with_new_user_basic_auth
    ):
        url = reverse("blog:api-v1:post_delete", args=[new_post.pk])
        response: Response = api_client_with_new_user_basic_auth.delete(url)
        assert status.HTTP_403_FORBIDDEN == response.status_code

    @pytest.mark.it("작성자가 삭제 요청하면 성공")
    @pytest.mark.django_db
    def test_author_can_delete_post(self, faker):
        password = faker.password()
        user = create_user(raw_password=password)
        new_post = PostFactory(author=user)

        url = reverse("blog:api-v1:post_delete", args=[new_post.pk])
        apiclient = get_api_client_with_basic_auth(user, password)
        response = apiclient.delete(url)
        assert status.HTTP_204_NO_CONTENT == response.status_code

        # 삭제 요청이 정상적으로 처리되었으면 ObjectDoesNoteExist 예외가 발생해야 함
        with pytest.raises(ObjectDoesNotExist):
            Post.objects.get(pk=new_post.pk)
