# 회원가입 폼 만지기 
from django import forms 
from .models import *
from hirestaurant.models import * 

# class SignupForm(forms.ModelForm):
#     class Meta:
#         model=User 
#         fields = ["nickname"]
#     def signup(self,request,user):
#         user.nickname = self.cleaned_data["nickname"]
#         user.save() 
# 이후 settings.py에 추가해줘야 한다. 
# ACCOUNT_SIGNUP_FORM_CLASS = "hirestaurant.forms.SignupForm"


# 후기 작성 폼 

class ReviewForm(forms.ModelForm):
    # Restaurant 모델의 restaurant_name을 선택하는 필드 추가
    restaurant_info = forms.ModelChoiceField(
        queryset=Restaurant.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Restaurant Name'  # 필드 레이블 설정
    )
    
    class Meta:
        model = Review
        fields = [
            "title",
            "restaurant_link",
            "rating",
            "image1",
            "image2",
            "image3",
            "content",
            'restaurant_info'
        ]
    
        widgets = {
            "rating": forms.RadioSelect,
        } #choice들이 드롭다운이 아닌 라디오 셀렉트로 바뀐다
        

# 대댓글 폼 
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
        widgets = { 
            'content': forms.Textarea,
        }
        
        
# 프로필 수정 폼 
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = [
            "nickname",
            "profile_pic",
            "intro" # 소개글이 들어가는데 디폴트 데이터값이 textinput이 들어간다 근데 용량이 매우 적음 
        ]
        widgets = {
            # 프로필 바꾸기 양식 
            "profile_pic": forms.FileInput,
            "intro" : forms.Textarea # textarea로 데이터 크기를 맞춰줌 
        }