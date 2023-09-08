from django.db.models.query import QuerySet
from django.shortcuts import render
from django.urls import reverse
from allauth.account.views import PasswordChangeView
from django.views.generic import (
    View,
    ListView,
    DeleteView,
    CreateView,
    UpdateView,
    DetailView,
)

from django.shortcuts import get_object_or_404

from hirestaurant.models import * 
from hirestaurant.forms import * 

# 접근제한자
from django.db.models import Q 
from django.contrib.contenttypes.models import ContentType
from typing import Any, Dict, List 



# 시작페이지
def index(request):
    # Review 모델에서 리뷰 객체들을 가져옵니다. 필터링 등으로 원하는 리뷰를 가져올 수 있습니다.
    reviews = Review.objects.all()
    return render(request, 'main/index.html', {'reviews': reviews})



class ReviewIndexView(ListView):
    model = Review
    template_name = "main/review_list.html"
    paginate_by = 4 
    context_object_name = "reviews"
    ordering = ["-dt_created"] # 생성일 기준 내림차순

class RestaurantList(ListView):
    model = Restaurant
    template_name = "main/restraunt_list.html"
    context_object_name = "restraunt_list"
    paginate_by = 4


# Review Detail 
class ReviewDetailView(DeleteView):
    mdoel = Review
    template_name = "main/review_detail.html"
    pk_url_kwarg = "review_id" # 리뷰의 고유값 id 


# Create Review 

class ReviewCreateView(CreateView):
    model = Review 
    form_class = ReviewForm
    template_name = "main/review_form.html"
    
    def form_valid(self, form):
        # 사용자와 리뷰를 연결
        form.instance.author = self.request.user
        
        # restaurant_name 필드에서 선택된 식당을 가져와서 리뷰와 연결
        restaurant_name = form.cleaned_data['restaurant_info'] 
        restaurant = get_object_or_404(Restaurant, restaurant_name=restaurant_name)
        form.instance.restaurant_info = restaurant
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})


# Review Detail 

class ReviewDetailVeiw(DetailView):
    model = Review
    template_name = "main/review_detail.html"
    pk_url_kwarg = "review_id" # 상세페이지 구축 링크를 게시물 고유 번호인 id값으로 변환  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 코멘트 영역은 다음에 
        # context['form'] = CommentForm()
        # context['review_ctype_id'] = ContentType.objects.get(model='review').id
        # context['comment_ctype_id'] = ContentType.objects.get(model='comment').id
        
        # 유저가 좋아요 기능을 했는지 안 했는지 구별하기 만들기 
        # user =self.request.user
        
        # if user.is_authenticated:
        #     review = self.object # detailview 에서는 뷰가 다루고 있는 오브젝트를 다 가져올 수 있음
        #     context['likes_review'] = Like.objects.filter(user=user,review=review).exists()
        #     # 리뷰의 코멘트를 좋아요를 눌렀는지 안눌렀는지 확인하는 방법 
        #     context['liked_comments'] = Comment.objects.filter(review=review).filter(likes__user=user)
        #     #코멘트의 리뷰를 필터를해서 리뷰 안에 그 유저가 유저가 맞는지를 확인한다. 
            
        
        return context

# review update 
class ReviewUpdateViews(UpdateView):
    model = Review
    form_class = ReviewForm 
    template_name = "main/review_form.html"
    pk_url_kwarg = "review_id"
    
    def get_success_url(self):
        return reverse("review_detail",kwargs={"review_id":self.object.id}) 

# review Delete 

class ReviewDeleteView(DeleteView):
    model = Review 
    template_name = "main/review_confirm_delete.html"
    pk_url_kwarg = "review_id"
    
    
    def get_success_url(self):
        return reverse("review_list")
    

# 유저가 쓴 리뷰를 조회한다
class UserReviewListView(ListView):
    model = Review
    template_name = "main/user_review_list.html"
    context_object_name = "user_reviews"
    paginate_by = 4
    
    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Review.objects.filter(author__id = user_id).order_by("dt_created")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(User,id=self.kwargs.get("user_id"))
        context['profile_user'] = get_object_or_404(User,id=self.kwargs.get("user_id"))
        return context 
    
    
    
# profile view 
class ProfileVeiw(DetailView):
    model = User 
    template_name = "main/profile.html"
    pk_url_kwarg = "user_id"
    
    context_object_name = "profile_user"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("user_id")
        context['user_reviews'] = Review.objects.filter(author__id = user_id).order_by("-dt_created")[:4]
        return context 
    



# 패스워드 변경 커스텀 페이지 만들기
class CustomPasswordChangeView(PasswordChangeView):
    # 오버라이딩 
    # 상속된 속성에 내용을 덧붙여서 다르게 사용 
    # 변경이 완료되면 리다이렉트 해주는 함수
    def get_success_url(self): 
        return reverse("index")
    
    
    


