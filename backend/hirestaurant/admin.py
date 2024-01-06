from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import * 


class CommentInline(admin.StackedInline):
    model = Comment 
    
    
class LikeInline(GenericStackedInline):
    model = Like


class UserInline(admin.StackedInline):
    model = User.following.through
    fk_name = 'to_user'
    verbose_name = 'Follower'
    verbose_name_plural = 'Followers'

admin.site.register(User,UserAdmin) # 유저 모델의 정보를 모두 보여주길
UserAdmin.fieldsets += (('Custom fields',{'fields':('nickname','profile_pic','intro','following')}),)
# custom fields라는 섹션 아래에 nickname fields라는 필드를 새로 추가해줌
# 원래는 admin에 유저 abstract로 끌고온 유저 정보가 나오지 않으니 수동으로 추가 해줘야함
UserAdmin.inlines = (UserInline,)

admin.site.register(Restaurant)

    
class ReviewAdmin(admin.ModelAdmin):
    inlines = (
        CommentInline,
        LikeInline,
    )
    list_display = ('title', 'author')

class CommentAdmin(admin.ModelAdmin):
    inlines = (
        LikeInline,
    )


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
admin.site.register(Tag, TagAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Bookmark)

admin.site.register(Comment,CommentAdmin)

admin.site.register(Like,)

admin.site.register(Category)
