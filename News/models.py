from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Create your models here.
PUBLISH_CHOICES = (
    (0,'เผยแพร่'),
    (1, 'ไม่เผยแพร่'),
)

class News(models.Model) :
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = RichTextField()
    image = models.ImageField(upload_to='uploads/news_imgs')
    publish = models.IntegerField(choices=PUBLISH_CHOICES, default=0)
    date_created = models.DateTimeField(auto_now=True)