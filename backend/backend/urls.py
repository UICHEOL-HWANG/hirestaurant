from django.contrib import admin
from django.urls import path,include

# 이메일 인증 관련 
from django.views.generic import TemplateView #제네릭 뷰에 있는 템플릿 뷰를 가져온다
# 따로 view를 정의해주지 않아도 됨

# from coplate.views import CustomPasswordChangeView
from django.conf import settings
from django.conf.urls.static import static

# 비밀번호 찾기 가져오기 
from hirestaurant.views import CustomPasswordChangeView

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),
    
 
    # 이메일 인증 완료창
    path('email-confirmation-done/',
    TemplateView.as_view(template_name="account/email_confirmation_done.html")
    ,name="account_email_confirm"),
    # allauth 
    path('',include('allauth.urls')), # 회원가입 라이브러리인 allauth를 생성 
    
    # 비밀번호 변경 체인지
    path('password/change/',CustomPasswordChangeView.as_view(),name="account_password_change"),
    
    path('email-confirmation-required/',
    TemplateView.as_view(template_name="account/email_confirmation_required.html")
    ,name="account_email_confirmation_required"),
    
    #m ain_sites
    path('',include('hirestaurant.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 미디어 파일 업로드 시 필요
# handler403 = 'coplate.views.custom_permission_denied' # 나중에 홈페이지 영역 링크 침범시 오류 메세지 출력

