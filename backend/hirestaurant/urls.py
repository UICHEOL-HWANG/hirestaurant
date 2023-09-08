from django.urls import path 
from . import views 
from .models import * 

urlpatterns = [
    path('',views.index,name="index"),
    
    #식당 정보
    path('restraunt_list/',views.RestaurantList.as_view(),name='restraunt_list'),
    
    #리뷰 
    path('review_list/',views.ReviewIndexView.as_view(),name="review"),
    path('reviews/new/',views.ReviewCreateView.as_view(),name='review-create'),
    path('reviews/<int:review_id>/',views.ReviewDetailVeiw.as_view(),name='review-detail'),

    # 프로필 
    path('users/<int:user_id>/reviews/',
         views.ProfileVeiw.as_view(),
         name = "profile"
         ),
    
]
