from django.shortcuts import render
from News.models import News

# Create your views here.
def newsPage(request):
    news_obj = News.objects.all().order_by('-date_created')

    context = {
        'title': "ข่าวประชาสัมพันธ์",
        'subtitle': 'ข่าวประชาสัมพันธ์เรื่องทุเรียนภูเขาไฟ จังหวัดศรีสะเกษ',
        'news': news_obj,
    }
    return render(request, 'news_page.html', context)

def newsDetail(request, id):
    news_obj = News.objects.get(id=id)
    news_etc = News.objects.all().exclude(id=id).order_by('-date_created')[:10]
    context = {
        'title': news_obj.title ,
        'content': news_obj,
        'news_etc': news_etc,
    }
    return render(request, 'news_detail.html', context)