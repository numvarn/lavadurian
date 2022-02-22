from django.contrib import admin
from django import forms
from News.models import News
from ckeditor.widgets import CKEditorWidget

from django.contrib.auth.models import User

class NewsAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = News
        exclude = ['author', 'date_created']

class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ['title', 'author', 'publish', 'date_created']
    
    # Action save model
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(News, NewsAdmin)