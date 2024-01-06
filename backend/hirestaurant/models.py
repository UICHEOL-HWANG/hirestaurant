from django.db import models
from django.contrib.auth.models import AbstractUser # 회원 모델 
from .validators import * 
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class User(AbstractUser): # AbstractUser 모델 상속 
    nickname = models.CharField(max_length=15,unique=True,null=True,
                                error_messages= {'unique':'이미 사용중인 닉네임'}
                                ) # 중복 닉네임 제한 
    
    profile_pic = models.ImageField(default="default_profile_pic.jpg",upload_to='profile_pics',
                                    blank=True
                                    ) # 유저 프로필사진 
    intro = models.CharField(max_length=60,blank=True)
    
    following = models.ManyToManyField('self',symmetrical=False,blank=True,related_name="followers",) #팔로우 팔로잉 관계 
    # 비대칭이다 A가 B를 팔로우 한다고 해서 
    # B가 A를 팔로우를 무조건 한다는 보장은 없으니까 
    # 그래서 symmetrical=False을 넣어준다 이해가 안가면 그냥 비대칭적인 관계를 설정해준다 이정도까지만 이해하자 
    # follow가 담긴 user 모델을 나중에 꺼내려면 user.user_set() 이 지랄로 복잡하게 꺼내야 하니
    # related_name = 옵션을 이용해서 역관계 명을 정의해주면 
    # user.followrs.all() 이런식으로 꺼내기 쉬워진다
    
    
    def __str__(self):
        return self.email
    # username은 무의하기 때문에 username대신 email을 보여준다
    # 왜냐하면 회원가입은 이메일로 하기 때문이다
    
#프로필 모델 
class Profile(models.Model):
    intro = models.CharField(max_length=60, blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nickname
    
    
# 태그와 카테고리 모델 

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    def __str__(self):
        return self.name
# 왜 만들었는지? → 추후에 식당 정보에서 얘네들끼리 정렬을 위해 만듬 

# 식당정보 모델 

class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    price_range = models.CharField(max_length=20)
    restaurant_image1 = models.ImageField(upload_to='restaurant_pics')
    restaurant_image2 = models.ImageField(upload_to='restaurant_pics',blank=True)
    restaurant_image3 = models.ImageField(upload_to='restaurant_pics',blank=True)
    
    likes = GenericRelation('Like',related_query_name="reivew")
    latitude = models.DecimalField(max_digits=9, decimal_places=6,default=0.0)  # 위도
    longitude = models.DecimalField(max_digits=9, decimal_places=6,default=0.0)  # 경도
    
    tags = models.ManyToManyField(Tag,blank=True) # ManyToManyField로 태그 연결
    categories = models.ManyToManyField(Category)
    
    def __str__(self):
        return self.restaurant_name
    
# 좋아요 모델 

class Like(models.Model): # content_type, object_id를 무조건 생성해야한다. 
    dt_created = models.DateTimeField(auto_now_add=True)
    
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="likes")
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # review = models.ForeignKey(Review, on_delete=models.CASCADE)  # 이 ForeignKey를 추가합니다.
    liked_object = GenericForeignKey() # 역관계는 직접 만들어줘야한다. set이 통하지 않음 
    # 제네릭 릴레이션을 만들어줘야함 
 
    
    def __str__(self):
        return f'({self.user},{self.liked_object})'


class Review(models.Model):
    title = models.CharField(max_length=30)
    restaurant_link = models.URLField(validators=[validate_restaurant_list],null=True)
    restaurant_info = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    RATING_CHOICE = [
        (1,"★"),
        (2,"★★"),
        (3,"★★★"),
        (4,"★★★★"),
        (5,"★★★★★"),
    ] # 평점 점수 5점까지
    
    rating = models.IntegerField(choices=RATING_CHOICE,default=None) #평점 
                                #default 옵션을 지정해서, listinlne을 초기화 시켜줌
    image1 = models.ImageField(upload_to="review_pics")
    image2 = models.ImageField(upload_to="review_pics",blank=True)                            
    image3 = models.ImageField(upload_to="review_pics",blank=True)                            
    content = models.TextField() # 리뷰 내용 
    dt_created = models.DateField(auto_now_add=True) # 리뷰 생성날짜 
    dt_updated = models.DateField(auto_now=True) #리뷰 수정 날짜
    
    #초기 평점 0점 특수문자 별로 표현한다 
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    likes = GenericRelation('Like',related_query_name="review")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-dt_created'] # 리뷰 생성 내림차순


# 대댓글 
class Comment(models.Model): # 리뷰 댓글 모델 
    content = models.TextField(max_length=500,blank=False) # 댓글 내용 / 500자 제한 / 빈값 불허용 
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments") # 유저가 삭제되면 유저가 게시한 코멘트도 다 삭제
    review = models.ForeignKey(Review,on_delete=models.CASCADE,related_name="comments") # 리뷰가 삭제되면 리뷰에 같이 담긴 코멘트들도 같이 삭제됨
    likes = GenericRelation('Like',related_query_name="comment")
    edited = models.BooleanField(default=False)  # 수정 여부 필드 추가

    
    def __str__(self):
        return self.content[:30] #30자만 출력 
    
    class Meta: # 모델 자체의 옵션 
        ordering = ['-dt_created'] # 리뷰들을 생성차 / 내림차순 

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} - {self.restaurant.restaurant_name}"