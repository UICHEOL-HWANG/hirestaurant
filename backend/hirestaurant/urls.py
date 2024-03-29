from django.urls import path 
from . import views 
from .models import * 

urlpatterns = [
    path('',views.index,name="index"),
    
    #식당 정보
    path('restraunt_list/',views.RestaurantList.as_view(),name='restraunt_list'),
    path('restaurant_list/<int:restaurant_id>/bookmark/', views.BookmarkView.as_view(), name='bookmark'),
    # 식당 태그 
    path('restaurants/tag/<str:tag>/', views.RestaurantListByTagView.as_view(), name='restaurant-list-by-tag'),
    #식당 상세정보 
    path('restaurant_detail/<int:restaurant_id>/',views.RestaurantDetail.as_view(),name="restaurant_detail"),
    #특정 카테고리만 모아보기 
    path('restaurants/category/<str:category_name>/',views.RestaurantByCategoryView.as_view(), name='category_page'),

    # 특정 식당의 리뷰 모아보기 
    path('restaurant/<int:restaurant_id>/',views.RestaurantDetailReviewList.as_view(), name='restaurant_reviews'),
    
    
    #추천시스템 
    path('users/<int:user_id>/recommendations/',views.RecommendedView.as_view(),name='recommend'),
    
    #리뷰 
    path('review_list/',views.ReviewIndexView.as_view(),name="review"),
    path('reviews/new/',views.ReviewCreateView.as_view(),name='review-create'),
    path('reviews/<int:review_id>/',views.ReviewDetailView.as_view(),name='review-detail'),
    path('reviews/<int:review_id>/edit/', views.ReviewUpdateViews.as_view(), name="review-update"),
    path('reviews/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    
    # 대댓글 
    path('reviews/<int:review_id>/comments/create/',views.CommentCreateView.as_view(),name='comment-create'),
    path('comments/<int:comment_id>/edit/', views.CommentUpdateView.as_view(), name='comment-update'), #
    path('comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
     
    # 프로필 
    path('users/<int:user_id>/',
         views.ProfileVeiw.as_view(),
         name = "profile"
         ),
    path('users/<int:user_id>/reviews/',views.UserReviewListView.as_view(),name="user-review-list"),
    
    # 프로필 설정 
    path('edit-profile/',views.ProfileUpdateView.as_view(),name="profile-update"),
    path('set-profile/',views.ProfileSetView.as_view(),name="profile-set"),
    
    
    #팔로잉 팔로워 
    
    path('user/<int:user_id>/follow/',views.ProcessFollowView.as_view(),name='process-follow'),
    
    # follow following page 
    path('users/<int:user_id>/following/', views.FollowingListView.as_view(), name='following-list'),
    path('users/<int:user_id>/followers/', views.FollowerListView.as_view(), name='follower-list'),
    
    # 좋아요
    path('like/<int:content_type_id>/<int:object_id>/',views.ProcessLikeView.as_view(),name="process-like"),
    
    path('user/<int:pk>/bookmarks/', views.BookmarkedRestaurantsView.as_view(), name='user_bookmarks'),

    
    
]
