from django import template
import datetime, pytz
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False

@register.filter(name='get_at_index')
def get_at_index(list, index):
    return list[index]

@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter(name='thai_time')
def thai_time(utc_date):
    if utc_date != '':
        tz = pytz.timezone('Asia/Bangkok')

        local_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(tz)
        now1 = tz.normalize(local_dt)

        month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[now1.month]
        thai_year = now1.year + 543
        time_str = now1.strftime('%H:%M')
        # time_str = now1.strftime('%H:%M:%S')
        
        return "%d %s %d %s"%(now1.day, month_name, thai_year, time_str) # 30 ตุลาคม 2560 20:45:30
    else:
        return '-'

@register.filter(name='print_timestamp')
def print_timestamp(timestamp):
    try:
        ts = int(timestamp / 1000)
    except ValueError:
        return None
    # return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # return datetime.datetime.fromtimestamp(ts)
    return datetime.datetime.fromtimestamp(ts)

@register.filter(name='print_api_date')
def print_api_date(date):
    d1 = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return d1.strftime('%d-%m-%Y')
