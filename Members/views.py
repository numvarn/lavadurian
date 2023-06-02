from django.shortcuts import HttpResponse, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.models import Group
from Members.models import Trader, registerGI

# Create your views here.


def userLogin(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('user'),
            password=request.POST.get('password')
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, 'This account has been disabled!')
                return render(request, 'login-social.html')
        else:
            messages.error(request, 'Error wrong username/password')
            return render(request, 'login-social.html')
    else:
        return render(request, 'login-social.html')


def passwordRecovery(request):
    return render(request, 'password-social.html')

# -----------------------------------------------------------------------------


def Logout(request):
    messages.error(request, 'User has been loged out')
    logout(request)
    return redirect('/members/login')

# -----------------------------------------------------------------------------


def registerCustomer(request):
    if request.method == 'POST':
        # name = request.POST.get('username')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        pass1 = request.POST.get('password1')

        if checkUserExist(email):
            user = User.objects.create_user(
                username=email,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=pass1,
            )

            my_group = Group.objects.get(name='customer')
            my_group.user_set.add(user)

            if user is not None:
                messages.error(request, 'User has been created.')
                return redirect('/members/login')
        else:
            messages.error(request, 'Username or Email is Already Exist')
            return render(request, 'register-customer.html')
        return render(request, 'register-customer.html')
    else:
        return render(request, 'register-customer.html')
# -----------------------------------------------------------------------------


def registerTrader(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        pass1 = request.POST.get('password1')

        if checkUserExist(email):
            user = User.objects.create_user(
                username=email,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=pass1,
            )

            my_group = Group.objects.get(name='trader')
            my_group.user_set.add(user)

            # add trader profile
            Trader.objects.create(
                account=user,
                citizen_id=request.POST.get('citizenid'),
                trader_type=request.POST.get('tradertype'),
                store_name=request.POST.get('tradername'),
                phone=request.POST.get('phone'),
            )

            if user is not None:
                messages.error(request, 'สร้างบัญชีผู้ค้าเรียบร้อย')
                return redirect('/members/login')
        else:
            messages.error(request, 'Username or Email is Already Exist')
            return render(request, 'register-store.html')
        return render(request, 'register-store.html')
    else:
        return render(request, 'register-store.html')
# -----------------------------------------------------------------------------
# Check User or Email is Already Exist


def checkUserExist(email):
    user = User.objects.filter(
        Q(username__icontains=email) |
        Q(email__icontains=email)
    )
    if len(user) != 0:
        return False
    else:
        return True

# -----------------------------------------------------------------------------


@login_required
def importRegisterGI(request):
    import csv
    from django.contrib.staticfiles import finders
    from datetime import datetime

    url = finders.find('csv/gi_register.csv')

    with open(url) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                if line_count > 0:
                    date_string = row[12].strip()
                    date_start = datetime.strptime(date_string, '%d/%m/%Y')

                    date_string = row[13].strip()
                    date_end = datetime.strptime(date_string, '%d/%m/%Y')

                    # area size
                    if row[10] == "":
                        row[10] = 0

                    if row[9] != "":
                        phone = '0'+row[9].strip()
                    else:
                        phone = ""

                    registerGI.objects.create(
                        prefix=row[1].strip(),
                        first_name=row[2].strip(),
                        last_name=row[3].strip(),
                        address=row[4].strip(),
                        moo=row[5].strip(),
                        subdistrict=row[6].strip(),
                        district=row[7].strip(),
                        province=row[8].strip(),
                        phone=phone,
                        area_size=row[10],
                        type=row[11].strip(),
                        date_start=date_start,
                        date_end=date_end,
                    )
                else:
                    break

                line_count += 1

    return HttpResponse("Import Success")
