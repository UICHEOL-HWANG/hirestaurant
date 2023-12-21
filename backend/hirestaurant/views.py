from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render,reverse,get_object_or_404,redirect
from django.urls import reverse,reverse_lazy
from allauth.account.views import PasswordChangeView
from django.views.generic import (
    View,
    ListView,
    DeleteView,
    CreateView,
    UpdateView,
    DetailView,
)

from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse,HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from typing import Any, Dict, List 


#CSRF
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from hirestaurant.models import * 
from hirestaurant.forms import * 
from hirestaurant.mixins import * 

# 접근제한자
from django.db.models import Q 
from django.contrib.contenttypes.models import ContentType
from typing import Any, Dict, List 

from django.http import HttpResponseForbidden,HttpResponse

def custom_permission_denied(request, exception):
    return render(request, 'account/403.html', status=403) # 비정상적인 접근을 막는 403 forbidden 커스텀 



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
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user = self.request.user
            if user.is_authenticated:
                bookmarked_restaurants = Bookmark.objects.filter(user=user).values_list('restaurant_id', flat=True)
                context['bookmarked_restaurants'] = bookmarked_restaurants
            return context

class RestaurantListByTagView(ListView):
    model = Restaurant
    template_name = "main/restaurant_list_by_tag.html"  # 해당 태그에 따른 식당 목록을 보여줄 템플릿 파일
    context_object_name = "restaurants"  # 템플릿에서 사용할 식당 목록 변수의 이름

    def get_queryset(self):
        tag = self.kwargs['tag']  # URL에서 전달된 태그 값 가져오기
        return Restaurant.objects.filter(tags__name=tag) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            bookmarked_restaurants = Bookmark.objects.filter(user=user).values_list('restaurant_id', flat=True)
            context['bookmarked_restaurants'] = bookmarked_restaurants
        return context



class BookmarkView(View):
    def post(self, request, restaurant_id):
        if request.user.is_authenticated:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, restaurant=restaurant)
            
            if not created:
                # 이미 북마크된 경우 토글하여 제거
                bookmark.delete()
        return redirect('restraunt_list')



class BookmarkedRestaurantsView(LoginAndVerificationRequiredMixin, View):
    template_name = 'main/bookmarked_restaurants.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_id = request.user.id # 해당 계정의 id을 받고 
            bookmarks = Bookmark.objects.filter(user=request.user) # 해당 계정이 북마크한 내역 추출 
            return render(request, self.template_name, {'bookmarks': bookmarks, 'profile_user_id': user_id})
            # 어떻게 보여줄거냐 html 코드 안에서 호출해줄 이름  
        else: 
            # 로그인되지 않은 사용자의 경우 로그인 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('account_login'))





# RestaurantDetail 

class RestaurantDetail(DetailView):
    model = Restaurant
    template_name = "main/restaurant_detail.html"
    pk_url_kwarg = "restaurant_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant_list'] = Restaurant.objects.all()  # 예시: 모든 레스토랑 가져오기
        return context


# 대댓글 만들기 



class CommentCreateView(LoginAndVerificationRequiredMixin,CreateView):
    http_method_names = ['post']
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.review = Review.objects.get(id=self.kwargs.get('review_id'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('review-detail',kwargs ={'review_id':self.kwargs.get('review_id')})
    

class CommentUpdateView(LoginAndOwnershipRequiredMixin,UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'main/comment_update_form.html'
    pk_url_kwarg = 'comment_id'
    
    def form_valid(self, form):
        # 수정 작업을 수행하기 전에 edited 값을 True로 설정
        self.object.edited = True
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('review-detail', kwargs={'review_id': self.object.review.id})


class CommentDeleteView(LoginAndOwnershipRequiredMixin,DeleteView):
    model = Comment
    template_name = 'main/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('review-detail', kwargs={'review_id': self.object.review.id})


# Create Review 

class ReviewCreateView(LoginAndVerificationRequiredMixin,CreateView):
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
        # 업로드된 파일을 처리
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})


# Review Detail 


class ReviewDetailView(DetailView):
    model = Review
    template_name = "main/review_detail.html"
    pk_url_kwarg = "review_id" # 상세페이지 구축 링크를 게시물 고유 번호인 id값으로 변환  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['review_ctype_id'] = ContentType.objects.get(model='review').id
        context['comment_ctype_id'] = ContentType.objects.get(model='comment').id
        
        # 유저가 좋아요 기능을 했는지 안 했는지 구별하기 만들기 
        user = self.request.user
        
        if user.is_authenticated:
            review = self.object # detailview 에서는 뷰가 다루고 있는 오브젝트를 다 가져올 수 있음
            context['likes_review'] = Like.objects.filter(user=user,review=review).exists()
            # 리뷰의 코멘트를 좋아요를 눌렀는지 안눌렀는지 확인하는 방법 
            context['liked_comments'] = Comment.objects.filter(review=review).filter(likes__user=user)
            #코멘트의 리뷰를 필터를해서 리뷰 안에 그 유저가 유저가 맞는지를 확인한다. 
            
        
        return context

# review update 
class ReviewUpdateViews(LoginAndOwnershipRequiredMixin ,UpdateView):
    model = Review
    form_class = ReviewForm 
    template_name = "main/review_form.html"
    pk_url_kwarg = "review_id"
    
    def get_success_url(self):
        return reverse("review-detail",kwargs={"review_id":self.object.id}) 

# review Delete 



class ReviewDeleteView(LoginAndOwnershipRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('review')

    def get_object(self, queryset=None):
        review_id = self.kwargs.get('review_id')  # URL에서 review_id를 가져옵니다.
        obj = Review.objects.get(pk=review_id)
        return obj

    def form_valid(self, form):
        review = self.get_object()

        # 여기에 권한 체크 로직 추가 (예: 현재 사용자가 리뷰 작성자인지 확인)
        if not self.request.user.is_authenticated or self.request.user != review.author:
            return JsonResponse({'error': '권한이 없습니다.'}, status=403)

        review.delete()

        return JsonResponse({'message': '삭제되었습니다.'}, status=204)

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
    
# 특정 식당의 리뷰만 모아준다 

class RestaurantDetailReviewList(ListView):
    model = Review 
    template_name = "main/restaurant_detail_review_list.html"
    context_object_name = "restaurant_review_list"
    paginate_by = 4
    
    def get_queryset(self):
        # URL에서 식당의 ID 값을 가져옵니다.
        restaurant_id = self.kwargs['restaurant_id']
        
        # 해당 식당의 리뷰만 필터링하여 반환합니다.
        queryset = Review.objects.filter(restaurant_info_id=restaurant_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # URL에서 식당의 ID 값을 가져옵니다.
        restaurant_id = self.kwargs['restaurant_id']
        
        # 식당 정보를 가져와 context에 추가합니다.
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        context['restaurant'] = restaurant
        
        return context
        
    
    
# profile view 
class ProfileVeiw(DetailView):
    model = User 
    template_name = "main/profile.html"
    pk_url_kwarg = "user_id"
    
    context_object_name = "profile_user"
    
    def get_context_data(self,**kwargs): # 최신 4개의 리뷰를 profile 템플릿에 전달해줌
        context = super().get_context_data(**kwargs)
        # 팔로잉 여부 확인 
        user = self.request.user
        profile_user_id = self.kwargs.get('user_id')
        if user.is_authenticated:
            context['is_following'] = user.following.filter(id=profile_user_id).exists() #만약 좋아요를 눌러줬다면 
        # user_id = self.kwargs.get("user_id")
        context["user_reviews"] = Review.objects.filter(author__id=profile_user_id).order_by("-dt_created")[:4]
        # 내림차순 
        return context 
    

# 프로필 변경 페이지 

class ProfileUpdateView(UpdateView):
    model = User 
    form_class = ProfileForm 
    template_name = "main/profile_update_form.html"
    
    raise_exception = True # 접근자 제한 
    redirect_unauthenticated_users = False # 접근자 제한  
    
    def get_object(self,query=None):
        return self.request.user 
    
    def get_success_url(self):
        return reverse("profile",kwargs=({"user_id":self.request.user.id}))

    

# 초기 프로필 설정 (회원가입 했을 때)

class ProfileSetView(LoginRequiredMixin,UpdateView):
    model = User 
    form_class = ProfileForm 
    template_name = "main/profile_set_form.html"
    
    raise_exception = True # 접근자 제한 
    redirect_unauthenticated_users = False # 접근자 제한  
    
    def get_object(self,query=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse("index")


# 팔로잉 팔로워 페이지 

class FollowingListView(ListView):
    model = User
    template_name = 'main/following_list.html'
    context_object_name = 'following'
    paginate_by = 4

    def get_queryset(self):
        profile_user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        return profile_user.following.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user_id'] = self.kwargs.get('user_id')
        return context


class FollowerListView(ListView):
    model = User
    template_name = 'main/follower_list.html'
    context_object_name = 'followers'
    paginate_by = 4

    def get_queryset(self):
        profile_user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        return profile_user.followers.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user_id'] = self.kwargs.get('user_id')
        return context   


# 좋아요 프로세스 뷰 

@method_decorator(csrf_protect, name='dispatch')
class ProcessLikeView(LoginAndVerificationRequiredMixin,View): #로그인과 이메일 인증을 마쳐야 
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
            content_type_id = self.kwargs.get('content_type_id')
            object_id = self.kwargs.get('object_id')

            like, created = Like.objects.get_or_create(
                user=self.request.user,
                content_type_id=content_type_id,
                object_id=object_id,
            )

            if not created:
                like.delete()

            # 좋아요 개수 계산
            like_count = Like.objects.filter(content_type_id=content_type_id, object_id=object_id).count()

            # JSON 응답 생성
            response_data = {
                'liked': not created,
                'like_count': like_count,
                'like_text': '좋아요',  # 좋아요 텍스트를 서버에서 반환
            }

            return JsonResponse(response_data)


    
    # def post(self,request,*args,**kwargs):
    #     #self.kwargs.get('content_type_id')
    #     #self.kwargs.get('object_id')
    #     like,created = Like.objects.get_or_create(
    #         user = self.request.user, # 현재 유저 
    #         content_type_id = self.kwargs.get('content_type_id'), 
    #         object_id = self.kwargs.get('object_id'),
    #         # get_or_create 상기 건에 해당하는 오브젝트가 있으면 get, 즉시 가져오고 
    #         # 가져온 오브젝트를 like에 저장해준다 
    #         # create는 false가 됨 
    #         # 오브젝트가 없으면 True가 됨 
            
            
    #     ) # 좋아요를 눌렀는지 안눌렀는지 확인하기 
        
    #     if not created: # 만약 유저가 좋아요를 눌었으면 좋아요가 생성된 상태로 끝남 
    #         like.delete()
    #     return redirect(self.request.META['HTTP_REFERER'])

# 팔로우 프로세스 뷰 
    
class ProcessFollowView(LoginAndVerificationRequiredMixin,View): #로그인과 이메일 인증을 마쳐야 
    http_method_names = ['post']
    
    def post(self,request,*args,**kwargs):
        # 팔로잉 여부 확인 
        user = self.request.user
        profile_user_id = self.kwargs.get('user_id')
        if user.following.filter(id=profile_user_id).exists(): #만약 좋아요를 눌러줬다면 
            user.following.remove(profile_user_id) # 팔로잉 로직을 삭제해주고 
        else:
            user.following.add(profile_user_id) # 없으면 팔로잉 로직을 추가해줘라
        return redirect('profile',user_id=profile_user_id)

# 패스워드 변경 커스텀 페이지 만들기
class CustomPasswordChangeView(LoginRequiredMixin,PasswordChangeView):
    raise_exception = True # 접근자 제한 
    redirect_unauthenticated_users = False # 접근자 제한  
    # 오버라이딩 
    # 상속된 속성에 내용을 덧붙여서 다르게 사용 
    # 변경이 완료되면 리다이렉트 해주는 함수
    def get_success_url(self): # 비밀번호 변경이 성공적으로 변경 되면~
        return reverse('profile',kwargs={"user_id":self.request.user.id})
    
    
    


