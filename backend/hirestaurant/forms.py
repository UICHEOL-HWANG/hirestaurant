# 회원가입 폼 만지기 
from django import forms 
from .models import *
from hirestaurant.models import * 

class SignupForm(forms.ModelForm):
    class Meta:
        model=User 
        fields = ["nickname"]
    def signup(self,request,user):
        user.nickname = self.cleaned_data["nickname"]
        user.save() 
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
            "rating" : forms.RadioSelect,
        } #choice들이 드롭다운이 아닌 라디오 셀렉트로 바뀐다