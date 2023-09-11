from django.urls import path 
from . import views 
from .models import * 

urlpatterns = [
    path('',views.index,name="index"),
    
    #식당 정보
    path('restraunt_list/',views.RestaurantList.as_view(),name='restraunt_list'),
    
    #식당 상세정보 
    path('restaurant_detail/<int:restaurant_id>/',views.RestaurantDetail.as_view(),name="restaurant_detail"),
    
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
    
    # follow following page 
    path('users/<int:user_id>/following/', views.FollowingListView.as_view(), name='following-list'),
    path('users/<int:user_id>/followers/', views.FollowerListView.as_view(), name='follower-list'),
    
    # 좋아요
    path('like/<int:content_type_id>/<int:object_id>/',views.ProcessLikeView.as_view(),name="process-like"),
    
    
]
