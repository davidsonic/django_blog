from django.contrib import admin
from models import *     #newly add

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):    #self-defined model
    # fields=('title','desc','content')   #exclude
    list_display=('title','desc','content','date_publish',)

    fieldsets=(
        (None,{
            'fields': ('title','desc','content','user')
        }

        ),
        ('Advanced Options',{
            'classes': ('collapse',),
            'fields': ('click_count','is_recommend','category','tag','date_publish',)
        }

        )
    )

    #newly add
    class Media:
        js=(
            '/static/js/kindeditor-4.1.10/kindeditor-min.js',
            '/static/js/kindeditor-4.1.10/lang/zh_CN.js',
            '/static/js/kindeditor-4.1.10/config.js',
        )

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Links)
admin.site.register(Ad)
admin.site.register(Article,ArticleAdmin)  #admin.site.register(Article,ArticleAdmn)

