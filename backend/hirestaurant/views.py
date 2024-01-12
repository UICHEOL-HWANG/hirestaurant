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

# 추천시스템 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
    template_name = "main/restaurant_list.html"
    context_object_name = "restaurant_list"
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            bookmarked_restaurants = Bookmark.objects.filter(user=user).values_list('restaurant_id', flat=True)
            context['bookmarked_restaurants'] = bookmarked_restaurants

        # 각 식당별 태그 목록을 문자열로 변환하여 추가
        for restaurant in context['restaurant_list']:
            tags = restaurant.tags.all()
            restaurant.tag_list = ', '.join(tag.name for tag in tags)

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
        tag = self.kwargs['tag']  # 현재 태그를 컨텍스트에 추가
        context['current_tag'] = tag

        user = self.request.user
        if user.is_authenticated:
            bookmarked_restaurants = Bookmark.objects.filter(user=user).values_list('restaurant_id', flat=True)
            context['bookmarked_restaurants'] = bookmarked_restaurants
        return context

class RestaurantByCategoryView(ListView):
    model = Restaurant
    template_name = "main/restaurant_list_by_category.html"
    context_object_name = 'restaurants'

    def get_queryset(self):
        # URL에서 카테고리 이름을 가져옴
        category_name = self.kwargs.get('category_name')
        return Restaurant.objects.filter(categories__name=category_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_name = self.kwargs.get('category_name')
        context['selected_category'] = Category.objects.get(name=category_name)

        user = self.request.user
        if user.is_authenticated:
            bookmarked_restaurants = Bookmark.objects.filter(user=user).values_list('restaurant_id', flat=True)
            context['bookmarked_restaurants'] = bookmarked_restaurants

        for restaurant in context['restaurants']:
            category_names = restaurant.category_names.split(', ')
            restaurant.categories_list = Category.objects.filter(name__in=category_names)

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
    
    
## 추천시스템 

class RecommendedView(DetailView):
    model = User
    template_name = "main/recommendations.html"
    pk_url_kwarg = "user_id"
    context_object_name = "profile_user"
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # 사용자가 북마크한 식당을 가져옵니다.
        bookmarked_restaurants = Restaurant.objects.filter(bookmark__user=user)

        # 북마크한 식당의 카테고리 이름을 수집합니다.
        bookmarked_categories = Category.objects.filter(restaurant__in=bookmarked_restaurants).values_list('name', flat=True)

        # 모든 카테고리의 이름을 리스트로 가져옵니다.
        all_categories = list(Category.objects.values_list('name', flat=True))

        # TF-IDF 벡터라이저를 생성하고 모든 카테고리 데이터로 피팅합니다.
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_categories)

        # 북마크한 카테고리로 사용자 프로필 벡터를 생성합니다.
        user_profile_vector = vectorizer.transform(bookmarked_categories)

        # 코사인 유사도를 계산합니다.
        cosine_similarities = cosine_similarity(user_profile_vector, tfidf_matrix)

        # 유사도를 기반으로 식당을 정렬합니다.
        similar_indices = cosine_similarities.flatten().argsort()[-10:][::-1]

        # all_category_ids_list의 길이 확인
        all_category_ids_list = list(Category.objects.values_list('id', flat=True))
        len_all_categories = len(all_category_ids_list)

        # similar_indices의 각 인덱스가 len_all_categories 범위 내에 있는지 확인
        similar_indices = [i for i in similar_indices if i < len_all_categories]

        # 추천된 카테고리 ID를 구합니다.
        recommended_category_ids = [all_category_ids_list[i] for i in similar_indices]

        # 추천된 카테고리 ID에 해당하는 식당을 가져옵니다.
        recommended_restaurants = Restaurant.objects.filter(categories__id__in=recommended_category_ids).distinct()


        paginator = Paginator(recommended_restaurants, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            restaurants_page = paginator.page(page)
        except PageNotAnInteger:
            restaurants_page = paginator.page(1)
        except EmptyPage:
            restaurants_page = paginator.page(paginator.num_pages)

        context['page_obj'] = restaurants_page
        context['is_paginated'] = paginator.num_pages > 1
        
        # 여기서 recommended_restaurants를 page_obj로 대체
        # context['recommended_restaurants'] = recommended_restaurants
        # 대신 page_obj를 사용합니다:
        context['recommended_restaurants'] = restaurants_page.object_list
        return context