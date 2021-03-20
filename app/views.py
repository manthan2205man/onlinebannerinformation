# from django.core.validators import validate_email
from datetime import timedelta
from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from . forms import *
from . models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Avg
from validate_email import validate_email
from . paytm import Checksum
from django.views.decorators.csrf import csrf_exempt
from django.db.models import *

MERCHANT_KEY='tbQubBXKkCa5IloY'

today = datetime.date.today()

# order
@login_required(login_url='/login/')
def show_payment_done(request):
    data= Order_Banner.objects.filter(banner__publisher=request.user)
    return render(request, 'publisher/show_payment_done.html',{'data':data})

@login_required(login_url='/login/')
def update_mapdata(request,id):
    order=Order_Banner.objects.get(id=id)
    map=MapData.objects.get(id=order.mapdata.id)
    book=BookNow.objects.get(id=order.banner.id)
    map.photo=book.photo
    map.ad_type=book.ad_type
    map.save()
    book.pay_status='done'
    book.save()
    return redirect(show_payment_done)

@login_required(login_url='/login/')
def pay_order_banner(request,id):
    if request.method == 'POST':
        obj = Order_Banner.objects.get(id=id)
        s3 = request.user.first_name
        s4 = obj.banner.publisher.first_name
        s1 = s3.upper()
        s2 = s4.upper()
        print(s1[0] + s2)
        print(obj.id)
        orderid = s1[0] + s2 + str(obj.id)
        print(orderid)
        form = OrderBannerForm(request.POST, request.FILES,instance=obj)
        form = form.save(commit=False)
        form.unid = orderid
        form.save()
        return  redirect(order,id)
    else:
        obj = Order_Banner.objects.get(id=id)
        form = OrderBannerForm(request.POST, request.FILES, instance=obj)
        return render(request, 'customer/pay_order_banner.html', {'form': form})


@login_required(login_url='/login/')
def show_order_banner(request):
    data= Order_Banner.objects.filter(cus=request.user)
    return render(request, 'customer/show_order_banner.html',{'data':data})

@login_required(login_url='/login/')
def order_banner(request, id):
    if request.method == 'POST':
        data = BookNow.objects.get(id=id)
        form= OrderBannerForm(request.POST)
        form = form.save(commit=False)
        form.cus=request.user
        form.banner=data
        form.mapdata=data.mapdata
        a = data.mapdata.price
        b = data.days
        c = a * b
        form.pay = c
        form.save()
        return redirect(show_order_banner)
    else:
        form = OrderBannerForm(request.POST)
        return render(request, 'customer/order_banner.html', {'form': form})


@login_required(login_url='/login/')
def delete_order_banner(request,id):
    obj=Order_Banner.objects.get(id=id)
    obj.delete()
    return  redirect(show_order_banner)

# paytm


@login_required(login_url='/login/')
def order(request,id):
    obj = Order_Banner.objects.get(id=id)
    s1 = obj.unid
    s2 = obj.pay
    s3 = 10
    s4 = obj.cus.id

    print(s4)


    param_dict = {

        'MID': 'soObkr88054489271706',
        'ORDER_ID': str(s1),
        'TXN_AMOUNT': str(s2),
        'CUST_ID': '5',
        'INDUSTRY_TYPE_ID': 'Retail',
        'WEBSITE': 'WEBSTAGING',  # for testing
        'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

    }
    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)

    return render(request, 'payment/paytm.html', {'param_dict': param_dict})

@csrf_exempt
def handlerequest(request):  # paytm will send POST request herre
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a = response_dict['ORDERID']
            b = response_dict['TXNID']
            c = response_dict['BANKTXNID']
            d = response_dict['TXNDATE']
            obj = Order_Banner.objects.get(unid=a)
            print(obj)

            obj.status ='approved'
            obj.txnid = b
            obj.banktxnid = c
            obj.txndate = d
            obj.orderid = a
            obj.save()

            map = MapData.objects.get(id=obj.mapdata.id)
            map.status = 'Not Available'
            map.to_date = obj.banner.to_date+timedelta(days=1)
            map.save()

            book = BookNow.objects.get(id=obj.banner.id)
            book.pay_status = 'approved'
            book.save()
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'payment/paymentstatus.html', {'response': response_dict})

#rating
@login_required(login_url='/login/')
def rating(request):
    if request.method == 'POST':
        selected_rating = request.POST.get('star')
        print(selected_rating)
        form = RatingForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            if request.user.is_publisher == True:
                form.pub=request.user
            if request.user.is_customer == True:
                form.cus=request.user
            form.rate_us=selected_rating
            if Rating_Us.objects.filter(pub=request.user).exists() or Rating_Us.objects.filter(cus=request.user).exists():
                messages.error(request, 'Already Recorded your Rating')
                return redirect(rating)
            form.save()
            messages.success(request, 'Successfully Recorded your Rating')
            return redirect(homepage)
    else:
        form = RatingForm(request.POST)
        return render(request, 'rating/rating.html',{'form': form})

@login_required(login_url='/login/')
def pub_rating(request):
    if request.method == 'POST':
        selected_rating = request.POST.get('star')
        selected_pub = request.POST.get('publisher')
        publisher = User.objects.get(id=selected_pub)
        form = PubRatingForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            if request.user.is_customer == True:
                form.cus=request.user
                form.pub=publisher
                form.pub_rating=selected_rating
                if Rating_Us.objects.filter(cus=request.user,pub=publisher).exists():
                    messages.error(request, 'Already Recorded your Rating')
                    return redirect(pub_rating)
                form.save()
                messages.success(request, 'Successfully Recorded your Rating')
                return redirect(homepage)
    else:
        publisher = User.objects.filter(is_publisher=True)
        form = RatingForm(request.POST)
        return render(request, 'rating/pub_rating.html',{'form': form,'publisher':publisher})

# booking
@login_required(login_url='/login/')
def delete_booking(request,id):
    obj=BookNow.objects.get(id=id)
    obj.delete()
    return  redirect(show_my_booking)

@login_required(login_url='/login/')
def renew(request, id):
    banner1 = BookNow.objects.get(id=id)
    if request.method == 'POST':
        form = BookNowForm(request.POST,request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.customer = request.user
            form.publisher = banner1.publisher
            form.mapdata = banner1.mapdata
            form.status = 'pending'
            a = form.from_date
            b = form.to_date
            c = b - a
            days = c.days
            form.days = days

            order = Order_Banner.objects.values_list('mapdata', flat=True)
            order1 = BookNow.objects.values_list('mapdata', flat=True)
            order2 = Order_Banner.objects.filter(mapdata=id)
            print(order)
            print(order1)
            print(order2)

            if (set(order1) == set(order)):
                print(set(order1) == set(order))
                for i in order2:
                    print(i.banner.from_date)
                    if (i.banner.to_date > form.from_date):
                        print(i.banner.to_date <= form.from_date)
                        messages.error(request, 'Date Accupied')
                        return redirect(homepage)

            form.save()

            # sender_name = request.user.first_name
            # sender_email = request.user
            # message = "Sender Name:- {0}\n\n you have booking request from {0} \n\nSender email-id:- {2}".format(
            #     sender_name,['message'], sender_email)
            # send_mail('New booking request', message, banner.publisher, [banner.publisher],
            #           fail_silently=True)

            messages.success(request, 'Successfully Renew')
            return redirect(homepage)
    else:
        form = BookNowForm()
        return render(request, 'customer/renew.html', {'form': form,'data':banner1})

def show_my_booking(request):
    data= BookNow.objects.filter(customer=request.user)
    return render(request, 'customer/show_my_booking.html',{'data':data})

@login_required(login_url='/login/')
def booking_request(request):
    if request.method == 'POST':
        selected_start_date = request.POST.get('date')
        selected_end_date = request.POST.get('date1')
        print(selected_start_date)
        print(selected_end_date)
        data = BookNow.objects.filter(publisher=request.user,uploaded_date__range=[selected_start_date,selected_end_date])
        return render(request, 'publisher/booking_request.html', {'data': data})
    else:
        data=BookNow.objects.filter(publisher=request.user)
        return render(request, 'publisher/booking_request.html', {'data': data})

@login_required(login_url='/login/')
def booking_accept(request,id):
    obj=BookNow.objects.get(id=id)
    obj.status='approved'
    obj.save()

    # sender_name = request.user.first_name
    # sender_email = request.user
    # message = "Sender Name:- {0}\n\n your request for this banner is accepted through {0} :\n\nSender email-id:- {2}".format(
    #     sender_name, ['message'], sender_email)
    # send_mail('Booking Request Approved', message, obj.customer, [obj.customer],
    #           fail_silently=True)

    return redirect(booking_request)

@login_required(login_url='/login/')
def booking_reject(request,id):
    obj = BookNow.objects.get(id=id)
    obj.status = 'rejected'
    obj.save()

    # sender_name = request.user.first_name
    # sender_email = request.user
    # message = "Sender Name:- {0}\n\n your request for this banner is rejected through {0} :\n\nSender email-id:- {2}".format(
    #     sender_name, ['message'], sender_email)
    # send_mail('Booking Request rejected', message, obj.customer, [obj.customer],
    #           fail_silently=True)

    return redirect(booking_request)

@login_required(login_url='/login/')
def delete_location(request,id):
    obj=MapData.objects.get(id=id)
    obj.delete()
    return  redirect(surat_pub_map)

@login_required(login_url='/login/')
def view_location(request):
    data=MapData.objects.filter(publisher=request.user)
    return render(request, 'publisher/view_location.html',{'data':data})

@login_required(login_url='/login/')
def edit_location(request,id):
    if request.method == 'POST':
        obj = MapData.objects.get(id=id)
        form = MapDataForm(request.POST, request.FILES,instance=obj)
        if form.is_valid():
            form.save()
            return  redirect(view_location)
        else:
            obj = MapData.objects.get(id=id)
            form = MapDataForm(instance=obj)
            return render(request, 'publisher/add_marker.html', {'form': form})
    else:
        obj = MapData.objects.get(id=id)
        form = MapDataForm(instance=obj)
        return render(request, 'publisher/add_marker.html', {'form': form})




# banner compare
@login_required(login_url='/login/')
def delete_compare(request,id):
    obj=Compare_Banner.objects.get(id=id)
    obj.delete()
    return  redirect(show_add_compare)

@login_required(login_url='/login/')
def show_add_compare(request):
    data= Compare_Banner.objects.filter(cus=request.user)
    return render(request, 'customer/show_add_compare.html',{'data':data})

@login_required(login_url='/login/')
def add_compare(request, id):
    if request.method == 'POST':
        data = MapData.objects.get(id=id)
        form= CompareBannerForm(request.POST)
        form = form.save(commit=False)
        form.cus=request.user
        form.banner=data
        if not Compare_Banner.objects.filter(banner=data).exists():
            form.save()
            return redirect(show_add_compare)
        messages.error(request, 'Already in compare ')
        return redirect(homepage)
    else:
        form = CompareBannerForm(request.POST)
        return render(request, 'customer/add_compare.html', {'form': form})

# map
def compare_bharuch(request):
    if request.method!='POST':
        city = User.objects.values('city').distinct()
        data = MapData.objects.filter(publisher__city='Bharuch')
        publisher = User.objects.filter(is_publisher=True,city='Bharuch')
        return render(request, 'map/compare_bharuch.html',{'city':city,'data':data,'publisher':publisher})
    else:
        data = MapData.objects.all()
        publisher = User.objects.filter(is_publisher=True, city='Bharuch')
        selected_publisher1 = request.POST.get('publisher1')
        selected_publisher2 = request.POST.get('publisher2')
        if selected_publisher1 =='none' and selected_publisher2 =='none':
            return render(request, 'map/compare_bharuch.html', {'data': data, 'publisher': publisher})
        if selected_publisher2 =='none':
            pub1 = User.objects.get(id=selected_publisher1)
            data1 = MapData.objects.filter(publisher=pub1).count()
            price1 = MapData.objects.filter(publisher=pub1).aggregate(Avg('price'))
            return render(request, 'map/compare_bharuch.html',{'price1': price1, 'data1': data1, 'pub1': pub1,'data': data, 'publisher': publisher})

        if selected_publisher1 == 'none':
            pub2 = User.objects.get(id=selected_publisher2)
            data2 = MapData.objects.filter(publisher=pub2).count()
            price2 = MapData.objects.filter(publisher=pub2).aggregate(Avg('price'))
            return render(request, 'map/compare_bharuch.html', {'price2': price2, 'data2': data2,'pub2': pub2, 'data': data, 'publisher': publisher})
        else:
            pub1 = User.objects.get(id=selected_publisher1)
            pub2 = User.objects.get(id=selected_publisher2)
            data1= MapData.objects.filter(publisher=pub1).count()
            data2 = MapData.objects.filter(publisher=pub2).count()
            price1 = MapData.objects.filter(publisher=pub1).aggregate(Avg('price'))
            price2 = MapData.objects.filter(publisher=pub2).aggregate(Avg('price'))
            return render(request, 'map/compare_bharuch.html',{'price2':price2,'price1':price1,'data1':data1,'data2':data2,'pub1':pub1,'pub2':pub2,'data':data,'publisher':publisher})

def compare_surat(request):
    if request.method!='POST':
        city = User.objects.values('city').distinct()
        data = MapData.objects.filter(publisher__city='Surat')
        publisher = User.objects.filter(is_publisher=True,city='Surat')
        return render(request, 'map/compare_surat.html',{'city':city,'data':data,'publisher':publisher})
    else:
        data = MapData.objects.all()
        publisher = User.objects.filter(is_publisher=True, city='Surat')
        selected_publisher1 = request.POST.get('publisher1')
        selected_publisher2 = request.POST.get('publisher2')
        if selected_publisher1 =='none' and selected_publisher2 =='none':
            return render(request, 'map/compare_surat.html', {'data': data, 'publisher': publisher})
        if selected_publisher2 =='none':
            pub1 = User.objects.get(id=selected_publisher1)
            data1 = MapData.objects.filter(publisher=pub1).count()
            price1 = MapData.objects.filter(publisher=pub1).aggregate(Avg('price'))
            return render(request, 'map/compare_surat.html',{'price1': price1, 'data1': data1, 'pub1': pub1,'data': data, 'publisher': publisher})

        if selected_publisher1 == 'none':
            pub2 = User.objects.get(id=selected_publisher2)
            data2 = MapData.objects.filter(publisher=pub2).count()
            price2 = MapData.objects.filter(publisher=pub2).aggregate(Avg('price'))
            return render(request, 'map/compare_surat.html', {'price2': price2, 'data2': data2,'pub2': pub2, 'data': data, 'publisher': publisher})
        else:
            pub1 = User.objects.get(id=selected_publisher1)
            pub2 = User.objects.get(id=selected_publisher2)
            data1= MapData.objects.filter(publisher=pub1).count()
            data2 = MapData.objects.filter(publisher=pub2).count()
            price1 = MapData.objects.filter(publisher=pub1).aggregate(Avg('price'))
            price2 = MapData.objects.filter(publisher=pub2).aggregate(Avg('price'))
            return render(request, 'map/compare_surat.html',{'price2':price2,'price1':price1,'data1':data1,'data2':data2,'pub1':pub1,'pub2':pub2,'data':data,'publisher':publisher})

def bharuch_location_suggestion(request):
    if request.method!='POST':
        ad_data=MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        data1 = location.objects.filter(city='Bharuch')
        data = MapData.objects.filter(publisher__city='Surat')
        order = Order_Banner.objects.all()
        publisher = User.objects.filter(is_publisher=True,city='Bharuch')
        return render(request, 'map/bharuch_location_suggestion.html',{'order':order,'status_data':status_data,'ad_data':ad_data,'data':data,'data1':data1,'publisher':publisher})
    else:
        data1 = location.objects.filter(city='Bharuch')
        publisher = User.objects.filter(is_publisher=True, city='Bharuch')
        ad_data = MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        selected_status_data = request.POST.get('status')
        selected_location = request.POST.get('loation')
        selected_publisher = request.POST.get('publisher')
        selected_advertisement_types = request.POST.get('advertisement_types')
        selected_min_price=request.POST.get('min')
        selected_max_price = request.POST.get('max')
        maxprice = MapData.objects.filter(publisher__city='Bharuch').aggregate(Max('price'))
        max = maxprice["price__max"]
        minprice = MapData.objects.filter(publisher__city='Bharuch').aggregate(Min('price'))
        min = minprice["price__min"]

        if not selected_location =="none":
            if not selected_publisher == "none":
                if not selected_advertisement_types == "none":
                    if not selected_status_data == "none":
                        if not selected_min_price == "none":
                            pub = User.objects.get(id=selected_publisher)
                            loc = location.objects.get(id=selected_location)
                            data = MapData.objects.filter(publisher__city='Bharuch',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,price__range=(selected_min_price, max))
                            return render(request, 'map/bharuch_location_suggestion.html',
                                          {'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                                           'publisher': publisher})

                        pub = User.objects.get(id=selected_publisher)
                        loc = location.objects.get(id=selected_location)
                        data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,publisher__city='Surat')
                        return render(request, 'map/bharuch_location_suggestion.html',{'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                    pub = User.objects.get(id=selected_publisher)
                    loc = location.objects.get(id=selected_location)
                    data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,publisher__city='Surat')
                    return render(request, 'map/bharuch_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

                loc = location.objects.get(id=selected_location)
                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher=pub,publisher__city='Bharuch')
                return render(request, 'map/bharuch_location_suggestion.html',{'status_data':status_data,'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            loc = location.objects.get(id=selected_location)
            data = MapData.objects.filter(publisher__city='Bharuch')
            return render(request, 'map/bharuch_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

        if selected_location =="none":
            if selected_publisher == "none":
                if selected_advertisement_types == "none":
                    if selected_status_data == "none":
                        if selected_min_price == "none":
                            data = MapData.objects.filter(publisher__city='Bharuch')
                            messages.error(request, 'Please Select Options ')
                            return render(request, 'map/bharuch_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'data': data, 'data1': data1, 'publisher': publisher})


def surat_location_suggestion(request):
    if request.method!='POST':
        ad_data=MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        data1 = location.objects.filter(city='Surat')
        data = MapData.objects.filter(publisher__city='Surat')
        order = Order_Banner.objects.all()
        publisher = User.objects.filter(is_publisher=True,city='Surat')
        return render(request, 'map/surat_location_suggestion.html',{'order':order,'status_data':status_data,'ad_data':ad_data,'data':data,'data1':data1,'publisher':publisher})
    else:
        data1 = location.objects.filter(city='Surat')
        publisher = User.objects.filter(is_publisher=True, city='Surat')
        ad_data = MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        selected_status_data = request.POST.get('status')
        selected_location = request.POST.get('loation')
        selected_publisher = request.POST.get('publisher')
        selected_advertisement_types = request.POST.get('advertisement_types')
        selected_min_price=request.POST.get('min')
        selected_max_price = request.POST.get('max')
        maxprice = MapData.objects.filter(publisher__city='Surat').aggregate(Max('price'))
        max = maxprice["price__max"]
        minprice = MapData.objects.filter(publisher__city='Surat').aggregate(Min('price'))
        min = minprice["price__min"]

        if not selected_location =="none":
            if not selected_publisher == "none":
                if not selected_advertisement_types == "none":
                    if not selected_status_data == "none":
                        if not selected_min_price == "none":
                            pub = User.objects.get(id=selected_publisher)
                            loc = location.objects.get(id=selected_location)
                            data = MapData.objects.filter(publisher__city='Surat',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,price__range=(selected_min_price, max))
                            return render(request, 'map/surat_location_suggestion.html',
                                          {'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                                           'publisher': publisher})

                        pub = User.objects.get(id=selected_publisher)
                        loc = location.objects.get(id=selected_location)
                        data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,publisher__city='Surat')
                        return render(request, 'map/surat_location_suggestion.html',{'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                    pub = User.objects.get(id=selected_publisher)
                    loc = location.objects.get(id=selected_location)
                    data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,publisher__city='Surat')
                    return render(request, 'map/surat_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

                loc = location.objects.get(id=selected_location)
                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher=pub,publisher__city='Surat')
                return render(request, 'map/surat_location_suggestion.html',{'status_data':status_data,'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            loc = location.objects.get(id=selected_location)
            data = MapData.objects.filter(publisher__city='Surat')
            return render(request, 'map/surat_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

        if selected_location =="none":
            if selected_publisher == "none":
                if selected_advertisement_types == "none":
                    if selected_status_data == "none":
                        if selected_min_price == "none":
                            data = MapData.objects.filter(publisher__city='Surat')
                            messages.error(request, 'Please Select Options ')
                            return render(request, 'map/surat_location_suggestion.html',{'status_data':status_data,'ad_data': ad_data, 'data': data, 'data1': data1, 'publisher': publisher})



def surat_cus_map(request):
    if request.method!='POST':
        ad_data=MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        data1 = location.objects.filter(city='Surat')
        data = MapData.objects.filter(publisher__city='Surat')
        order = Order_Banner.objects.all()
        publisher = User.objects.filter(is_publisher=True,city='Surat')
        return render(request, 'map/surat_cus_map.html',{'order':order,'status_data':status_data,'ad_data':ad_data,'data':data,'data1':data1,'publisher':publisher})
    else:
        data1 = location.objects.filter(city='Surat')
        publisher = User.objects.filter(is_publisher=True, city='Surat')
        ad_data = MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        selected_status_data = request.POST.get('status')
        selected_location = request.POST.get('loation')
        selected_publisher = request.POST.get('publisher')
        selected_advertisement_types = request.POST.get('advertisement_types')
        selected_min_price=request.POST.get('min')
        selected_max_price = request.POST.get('max')
        maxprice = MapData.objects.filter(publisher__city='Surat').aggregate(Max('price'))
        max = maxprice["price__max"]
        minprice = MapData.objects.filter(publisher__city='Surat').aggregate(Min('price'))
        min = minprice["price__min"]

        # mam
        # if selected_location !="none":
        #     loc = location.objects.get(id=selected_location)
        #     return render(request, 'map/surat_cus_map.html',
        #                   {'loc':loc,'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
        #                    'publisher': publisher})
        #
        # if selected_status_data!="none":
        #     data = data.filter(status=selected_status_data)
        #
        # if selected_advertisement_types !="none":
        #     data = data.filter(ad_type=selected_advertisement_types)
        #
        # return render(request, 'map/surat_cus_map.html',
        #                   {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
        #                    'publisher': publisher})
        # pub = User.objects.filter(id=selected_publisher).first()
        #
        # loc = location.objects.filter(id=selected_location).first()
        # data = MapData.objects.filter(publisher=pub) | MapData.objects.filter(ad_type=selected_advertisement_types)

        #my code

        if not selected_location =="none":
            if not selected_publisher == "none":
                if not selected_advertisement_types == "none":
                    if not selected_status_data == "none":
                        if not selected_min_price == "none" and not selected_max_price == "none":
                            pub = User.objects.get(id=selected_publisher)
                            loc = location.objects.get(id=selected_location)
                            data = MapData.objects.filter(publisher__city='Surat',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,price__range=(selected_min_price, selected_max_price))
                            return render(request, 'map/surat_cus_map.html',
                                          {'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                                           'publisher': publisher})

                        pub = User.objects.get(id=selected_publisher)
                        loc = location.objects.get(id=selected_location)
                        data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,publisher__city='Surat')
                        return render(request, 'map/surat_cus_map.html',{'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                    pub = User.objects.get(id=selected_publisher)
                    loc = location.objects.get(id=selected_location)
                    data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,publisher__city='Surat')
                    return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

                loc = location.objects.get(id=selected_location)
                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher=pub,publisher__city='Surat')
                return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            loc = location.objects.get(id=selected_location)
            data = MapData.objects.filter(publisher__city='Surat')
            return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_publisher=="none":
            if not selected_advertisement_types == "none":
                if not selected_status_data == "none":
                    if not selected_min_price == "none" and not selected_max_price == "none":
                        pub = User.objects.get(id=selected_publisher)
                        data = MapData.objects.filter(publisher__city='Surat', publisher=pub, ad_type=selected_advertisement_types, status=selected_status_data,price__range=(selected_min_price, selected_max_price))
                        return render(request, 'map/surat_cus_map.html',
                                      {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

                    pub = User.objects.get(id=selected_publisher)
                    data = MapData.objects.filter(publisher__city='Surat',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data)
                    return render(request, 'map/surat_cus_map.html',{'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher__city='Surat',publisher=pub, ad_type=selected_advertisement_types)
                return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            pub = User.objects.get(id=selected_publisher)
            data = MapData.objects.filter(publisher__city='Surat',publisher=pub)
            return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_advertisement_types == "none":
            if not selected_status_data == "none":
                if not selected_min_price == "none" and not selected_max_price == "none":
                    data = MapData.objects.filter(publisher__city='Surat', ad_type=selected_advertisement_types,
                                                  status=selected_status_data,price__range=(selected_min_price, selected_max_price))
                    return render(request, 'map/surat_cus_map.html',
                                  {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                                   'publisher': publisher})

                data = MapData.objects.filter(publisher__city='Surat',ad_type=selected_advertisement_types,status=selected_status_data)
                return render(request, 'map/surat_cus_map.html',{'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

            data = MapData.objects.filter(publisher__city='Surat',ad_type=selected_advertisement_types)
            return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_status_data == "none":
            if not selected_min_price == "none" and not selected_max_price == "none":
                data = MapData.objects.filter(publisher__city='Surat', status=selected_status_data,price__range=(selected_min_price, selected_max_price))
                return render(request, 'map/surat_cus_map.html',
                              {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                               'publisher': publisher})

            data = MapData.objects.filter(publisher__city='Surat',status=selected_status_data)
            return render(request, 'map/surat_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_min_price == "none":
            if not selected_max_price == "none":
                data = MapData.objects.filter(publisher__city='Surat', price__range=(selected_min_price, selected_max_price))
                return render(request, 'map/surat_cus_map.html',
                              {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                               'publisher': publisher})

            data = MapData.objects.filter(publisher__city='Surat',price__range=(selected_min_price,max))
            return render(request, 'map/surat_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_max_price == "none":
            data = MapData.objects.filter(publisher__city='Surat',price__range=(min,selected_max_price))
            return render(request, 'map/surat_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_min_price == "none" and not selected_max_price == "none":
            data = MapData.objects.filter(publisher__city='Surat',price__range=(selected_min_price,selected_max_price))
            return render(request, 'map/surat_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                           'publisher': publisher})

        if selected_location =="none":
            if selected_publisher == "none":
                if selected_advertisement_types == "none":
                    if selected_status_data == "none":
                        data = MapData.objects.filter(publisher__city='Surat')
                        return render(request, 'map/surat_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data': data, 'data1': data1, 'publisher': publisher})



def bharuch_cus_map(request):
    if request.method!='POST':
        ad_data=MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        data1 = location.objects.filter(city='Bharuch')
        data = MapData.objects.filter(publisher__city='Bharuch')
        publisher = User.objects.filter(is_publisher=True,city='Bharuch')
        return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data':ad_data,'data':data,'data1':data1,'publisher':publisher})
    else:
        data1 = location.objects.filter(city='Bharuch')
        publisher = User.objects.filter(is_publisher=True, city='Bharuch')
        ad_data = MapData.objects.values('ad_type').distinct()
        status_data = MapData.objects.values('status').distinct()
        selected_status_data = request.POST.get('status')
        selected_location = request.POST.get('loation')
        selected_publisher = request.POST.get('publisher')
        selected_advertisement_types = request.POST.get('advertisement_types')
        selected_min_price=request.POST.get('min')
        selected_max_price = request.POST.get('max')
        maxprice = MapData.objects.filter(publisher__city='Bharuch').aggregate(Max('price'))
        max = maxprice["price__max"]
        minprice = MapData.objects.filter(publisher__city='Bharuch').aggregate(Min('price'))
        min = minprice["price__min"]

        if not selected_location =="none":
            if not selected_publisher == "none":
                if not selected_advertisement_types == "none":
                    if not selected_status_data == "none":
                        if not selected_min_price == "none" and not selected_max_price == "none":
                            pub = User.objects.get(id=selected_publisher)
                            loc = location.objects.get(id=selected_location)
                            data = MapData.objects.filter(publisher__city='Bharuch',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,price__range=(selected_min_price, selected_max_price))
                            return render(request, 'map/bharuch_cus_map.html',
                                          {'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                                           'publisher': publisher})

                        pub = User.objects.get(id=selected_publisher)
                        loc = location.objects.get(id=selected_location)
                        data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data,publisher__city='Bharuch')
                        return render(request, 'map/bharuch_cus_map.html',{'loc': loc, 'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                    pub = User.objects.get(id=selected_publisher)
                    loc = location.objects.get(id=selected_location)
                    data = MapData.objects.filter(publisher=pub, ad_type=selected_advertisement_types,publisher__city='Bharuch')
                    return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

                loc = location.objects.get(id=selected_location)
                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher=pub,publisher__city='Bharuch')
                return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            loc = location.objects.get(id=selected_location)
            data = MapData.objects.filter(publisher__city='Bharuch')
            return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_publisher=="none":
            if not selected_advertisement_types == "none":
                if not selected_status_data == "none":
                    pub = User.objects.get(id=selected_publisher)
                    data = MapData.objects.filter(publisher__city='Bharuch',publisher=pub, ad_type=selected_advertisement_types,status=selected_status_data)
                    return render(request, 'map/bharuch_cus_map.html',{'status_data': status_data, 'ad_data': ad_data, 'data1': data1,'data': data, 'publisher': publisher})

                pub = User.objects.get(id=selected_publisher)
                data = MapData.objects.filter(publisher__city='Bharuch',publisher=pub, ad_type=selected_advertisement_types)
                return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

            pub = User.objects.get(id=selected_publisher)
            data = MapData.objects.filter(publisher__city='Bharuch',publisher=pub)
            return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_advertisement_types == "none":
            if not selected_status_data == "none":
                data = MapData.objects.filter(publisher__city='Bharuch',ad_type=selected_advertisement_types,status=selected_status_data)
                return render(request, 'map/bharuch_cus_map.html',{'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

            data = MapData.objects.filter(publisher__city='Bharuch',ad_type=selected_advertisement_types)
            return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data1': data1, 'data': data, 'publisher': publisher})

        if not selected_status_data == "none":
            data = MapData.objects.filter(publisher__city='Bharuch',status=selected_status_data)
            return render(request, 'map/bharuch_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_min_price == "none":
            data = MapData.objects.filter(publisher__city='Bharuch',price__range=(selected_min_price,max))
            return render(request, 'map/bharuch_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_max_price == "none":
            data = MapData.objects.filter(publisher__city='Bharuch',price__range=(min,selected_max_price))
            return render(request, 'map/bharuch_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,'publisher': publisher})

        if not selected_min_price == "none" and not selected_max_price == "none":
            data = MapData.objects.filter(publisher__city='Bharuch',price__range=(selected_min_price,selected_max_price))
            return render(request, 'map/bharuch_cus_map.html',
                          {'status_data': status_data, 'ad_data': ad_data, 'data1': data1, 'data': data,
                           'publisher': publisher})

        if selected_location =="none":
            if selected_publisher == "none":
                if selected_advertisement_types == "none":
                    if selected_status_data == "none":
                        data = MapData.objects.filter(publisher__city='Bharuch')
                        return render(request, 'map/bharuch_cus_map.html',{'status_data':status_data,'ad_data': ad_data, 'data': data, 'data1': data1, 'publisher': publisher})


@login_required(login_url='/login/')
def surat_pub_map(request):
    if request.user.city=="Bharuch":
        return redirect(bharuch_pub_map)
    else:
        if request.method!='POST':
            ad_data=MapData.objects.values('ad_type').distinct()
            data1 = location.objects.filter(city='Surat')
            data = MapData.objects.filter(publisher=request.user)
            return render(request, 'map/surat_pub_map.html', {'data': data,'ad_data':ad_data,'data1':data1})

        else:
            ad_data = MapData.objects.values('ad_type').distinct()
            selected_location = request.POST.get('loation')
            selected_advertisement_types = request.POST.get('advertisement_types')

            if not selected_location =="none":
                if not selected_advertisement_types == "none":
                    loc = location.objects.get(id=selected_location)
                    data1 = location.objects.filter(city='Surat')
                    data = MapData.objects.filter(publisher=request.user,ad_type=selected_advertisement_types)
                    return render(request, 'map/surat_pub_map.html',{'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data})

                loc = location.objects.get(id=selected_location)
                data1 = location.objects.filter(city='Surat')
                data = MapData.objects.filter(publisher=request.user)
                return render(request, 'map/surat_pub_map.html',{'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data})

            if not selected_advertisement_types == "none":
                data1 = location.objects.filter(city='Surat')
                data = MapData.objects.filter(publisher=request.user,ad_type=selected_advertisement_types)
                return render(request, 'map/surat_pub_map.html',{'ad_data': ad_data, 'data1': data1, 'data': data})


@login_required(login_url='/login/')
def bharuch_pub_map(request):
    if request.method != 'POST':
        ad_data = MapData.objects.values('ad_type').distinct()
        data1 = location.objects.filter(city='Bharuch')
        data = MapData.objects.filter(publisher=request.user)
        return render(request, 'map/bharuch_pub_map.html', {'data': data, 'ad_data': ad_data, 'data1': data1})

    else:
        ad_data = MapData.objects.values('ad_type').distinct()
        selected_location = request.POST.get('loation')
        selected_advertisement_types = request.POST.get('advertisement_types')

        if not selected_location == "none":
            if not selected_advertisement_types == "none":
                loc = location.objects.get(id=selected_location)
                data1 = location.objects.filter(city='Bharuch')
                data = MapData.objects.filter(publisher=request.user, ad_type=selected_advertisement_types)
                return render(request, 'map/bharuch_pub_map.html',
                              {'ad_data': ad_data, 'loc': loc, 'data1': data1, 'data': data})

            loc = location.objects.get(id=selected_location)
            data1 = location.objects.filter(city='Surat')
            data = MapData.objects.filter(publisher=request.user)
            return render(request, 'map/bharuch_pub_map.html',
                          {'loc': loc, 'ad_data': ad_data, 'data1': data1, 'data': data})

        if not selected_advertisement_types == "none":
            data1 = location.objects.filter(city='Surat')
            data = MapData.objects.filter(publisher=request.user, ad_type=selected_advertisement_types)
            return render(request, 'map/bharuch_pub_map.html', {'ad_data': ad_data, 'data1': data1, 'data': data})




# save for later
@login_required(login_url='/login/')
def save_banner_map(request):
    data= Save_Banner.objects.filter(cus=request.user)
    return render(request, 'map/save_banner_map.html',{'data':data})

@login_required(login_url='/login/')
def show_save_banner(request):
    data= Save_Banner.objects.filter(cus=request.user)
    return render(request, 'customer/show_save_banner.html',{'data':data})

@login_required(login_url='/login/')
def delete_save_banner(request,id):
    obj=Save_Banner.objects.get(id=id)
    obj.delete()
    return  redirect(save_banner_map)

@login_required(login_url='/login/')
def save_banner(request,id):
    if request.method == 'POST':
        data = MapData.objects.get(id=id)
        form= SaveBannerForm(request.POST)
        form = form.save(commit=False)
        form.cus=request.user
        form.banner=data
        if not Save_Banner.objects.filter(banner=data).exists():
            form.save()
            return redirect(save_banner_map)
        messages.error(request, 'Already Saved ')
        return redirect(homepage)
    else:
        form = SaveBannerForm(request.POST)
        return render(request, 'customer/save_banner.html', {'form': form})


@login_required(login_url='/login/')
def booknow(request,id):
    if request.method == 'POST':
        banner1 = MapData.objects.get(id=id)
        form = BookNowForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.customer = request.user
            form.publisher=banner1.publisher
            form.mapdata=banner1
            form.status='pending'
            a = form.from_date
            b = form.to_date
            c = b - a
            days = c.days
            form.days=days

            order = Order_Banner.objects.values_list('mapdata',flat=True)
            order1 = BookNow.objects.values_list('mapdata',flat=True)
            order2 = Order_Banner.objects.filter(mapdata=id)
            print(order)
            print(order1)
            print(order2)

            if (set(order1) == set(order)):
                print(set(order1) == set(order))
                for i in order2:
                    print(i.banner.from_date)
                    if(i.banner.to_date > form.from_date):
                        print(i.banner.to_date <= form.from_date)
                        messages.error(request, 'Date Accupied')
                        return redirect(homepage)

            form.save()

            # sender_name = request.user.first_name
            # sender_email = request.user
            # message = "Sender Name:- {0}\n\n you have booking request from {0} \n\nSender email-id:- {2}".format(
            #     sender_name,['message'], sender_email)
            # send_mail('New booking request', message, banner.publisher, [banner.publisher],
            #           fail_silently=True)

            messages.success(request, 'Successfully Booked')
            return redirect(homepage)
        else:
            form = BookNowForm()
            messages.error(request, 'Invalid ')
            return render(request, 'customer/booknow.html', {'form': form})
    else:
        banner=MapData.objects.get(id=id)
        today = datetime.date.today()
        form = BookNowForm()#initial = {'customer': request.user.first_name,'publisher': banner.publisher.first_name})
        return render(request, 'customer/BookNow.html', {'today':today,'form': form,'data':banner})


@login_required(login_url='/login/')
def add_marker(request):
    if request.method == 'POST':

        data1 = location.objects.filter(city='Surat')
        selected_location = request.POST.get('loation')
        form = MapDataForm(request.POST,request.FILES)
        if form.is_valid():
            form=form.save(commit=False)
            form.publisher=request.user
            form.save()
            messages.success(request, 'Successfully')
            return redirect(homepage)
        else:
            if request.user.city=="Surat":
                data1 = location.objects.filter(city='Surat')
            if request.user.city=="Bharuch":
                data1 = location.objects.filter(city='Bharuch')
                
            selected_location = request.POST.get('loation')
            if not selected_location == "none":
                loc = location.objects.get(id=selected_location)
                form = MapDataForm()
                return render(request, 'publisher/add_marker.html',
                              {'loc': loc, 'data1': data1, 'form': form})

            form = MapDataForm()
            messages.error(request, 'Invalid ')
            return render(request, 'publisher/add_marker.html', {'form': form})
    else:
        if request.user.city == "Surat":
            data1 = location.objects.filter(city='Surat')
        if request.user.city == "Bharuch":
            data1 = location.objects.filter(city='Bharuch')
        form = MapDataForm()
        return render(request, 'publisher/add_marker.html', {'form': form,'data1':data1})

# login
def pub_register(request):
    if request.method == 'POST':
        form = PublishersForm(request.POST,request.FILES)
        if form.is_valid():
            form=form.save(commit=False)
            form.is_publisher=True

            # email = form.username
            # is_valid = validate_email(email, verify=True)
            # print(is_valid)
            # if is_valid != True:
            #     messages.error(request, 'email wrong')
            #     return redirect(cus_register)
            #
            # if is_valid == True:
            #     User.objects.get(email=form.username)
            #     messages.error(request, 'e-mail taken')
            #     return redirect(cus_register)

            form.email = form.username
            form.is_active=False
            form.save()
            messages.success(request, 'Account Created Successfully')
            return redirect(login_page)
        else:
            form = PublishersForm()
            messages.error(request, 'Invalid ')
            return render(request, 'publisher/pub_register.html', {'form': form})
    else:
        form = PublishersForm()
        return render(request, 'publisher/pub_register.html', {'form': form})

def cus_register(request):
    if request.method == 'POST':
        form = CustomersForm(request.POST)

        if form.is_valid():
            form=form.save(commit=False)
            form.is_customer=True

            # email=form.username
            # is_valid = validate_email(email, verify=True)
            # print(is_valid)
            # if is_valid != True:
            #     messages.error(request, 'email wrong')
            #     return redirect(cus_register)
            #
            # if is_valid == True:
            #     User.objects.get(email=form.username)
            #     messages.error(request, 'e-mail taken')
            #     return redirect(cus_register)

            form.email = form.username
            form.save()
            messages.success(request,'Account Created Successfully')
            return redirect(login_page)
        else:
            form = CustomersForm()
            messages.error(request, 'Invalid ')
            return render(request, 'customer/cus_register.html', {'form': form})
    else:
        form = CustomersForm()
        return render(request, 'customer/cus_register.html', {'form': form})

def login_page(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        data = User.objects.filter(username=username,is_active=False)
        print(data)
        for i in data:
            if(username==i.username):
                messages.error(request, 'Account is not Activated')
                return render(request, 'signin/login.html')
        if user:
            login(request, user)
            if request.user.is_customer==True:
                return redirect(homepage)
            else:
                return redirect(homepage)
        else:
            messages.error(request,'Invalid email or Password')
            return render(request, 'signin/login.html')
    else:
        return render(request,'signin/login.html')

@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(login_page)
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect(login_page)
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'signin/password_change.html', {'form': form})

@login_required(login_url='/login/')
def cus_edit_profile(request):
    if request.method == 'POST':
        form = CusEditProfile(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(homepage)
    else:
        form = CusEditProfile(instance=request.user)
        return render(request, 'customer/cus_edit_profile.html', {'form':form})

@login_required(login_url='/login/')
def pub_edit_profile(request):
    if request.method == 'POST':
        form = PubEditProfile(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(homepage)
    else:
        form = PubEditProfile(instance=request.user)
        return render(request, 'publisher/pub_edit_profile.html', {'form':form})

@login_required(login_url='/login/')
def feedback(request):
    if request.method == 'POST':
        form = ContactForm(request.POST,initial={'name': request.user.first_name,'email': request.user.username })
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']
            message = "Sender Name:- {0}\n\n{0} has sent you a new message:\n\n{1}\n\nSender email-id:- {2}".format(sender_name, form.cleaned_data['message'],sender_email)
            send_mail('New Enquiry', message, 'bhavsarmanthan10@gmail.com', ['bhavsarmanthan10@gmail.com'],fail_silently=True)
            messages.success(request, 'Your feedback successfully Send to us')
            return redirect(homepage)
        else:
            form = ContactForm(initial={'name': request.user.first_name,'email': request.user.username})
            messages.error(request, 'Invalid ')
            return render(request, 'signin/feedback.html', {'form': form})
    else:
        form = ContactForm(initial={'name': request.user.first_name,'email': request.user.username})
        return render(request, 'signin/feedback.html', {'form': form})


@login_required(login_url='/login/')
def delete_account(request):
    if request.method == 'POST':
        delete_form = UserDeleteForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect(homepage)
    else:
        delete_form = UserDeleteForm(instance=request.user)

    context = {
        'delete_form': delete_form
    }

    return render(request, 'signin/delete_account.html', context)

def enquiry(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']
            message = "Enquiry From User which is not login \n\nSender Name:- {0}\n\n{0} has sent you a new message:\n\n{1}\n\nSender email-id:- {2}".format(sender_name, form.cleaned_data['message'],sender_email)
            send_mail('New Enquiry', message, 'bhavsarmanthan10@gmail.com', ['bhavsarmanthan10@gmail.com'],fail_silently=True)
            messages.success(request, 'Your enquiry/message successfully Send to us')
            return redirect(homepage)
        else:
            form = ContactForm()
            messages.error(request, 'Invalid ')
            return render(request, 'signin/enquiry.html', {'form': form})
    else:
        form = ContactForm()
        return render(request, 'signin/enquiry.html', {'form': form})


@login_required(login_url='/login/')
def logout_user(request):
    obj = Compare_Banner.objects.all()
    obj.delete()
    # obj1 = Order_Banner.objects.all()
    # obj1.delete()
    # obj2 = BookNow.objects.all()
    # obj2.delete()
    logout(request)
    return redirect(login_page)

def homepage(request):
    MapData.objects.filter(status='Not Available', to_date__lte=today).update(status='Available')
    return render(request, 'index.html')

# notification
@login_required(login_url='/login/')
def new_not(request):
    if request.user.is_superuser==True:
        new_publisher=User.objects.filter(is_publisher=True,is_active=False).values('first_name')
        print(new_publisher)
        return JsonResponse({'record': list(new_publisher)})

    if request.user.is_publisher==True:
        new_book=BookNow.objects.filter(publisher=request.user,status='pending').values('customer__first_name')
        print(new_book)
        return JsonResponse({'record':list(new_book)})

    if request.user.is_customer==True:
        new_book = BookNow.objects.filter(customer=request.user, status='approved',pay_status='pending').values('publisher__first_name','status') |  BookNow.objects.filter(customer=request.user, status='rejected').values('publisher__first_name', 'status')
        print(new_book)
        return JsonResponse({'record': list(new_book)})

@login_required(login_url='/login/')
def newUpdate(request):
    if request.user.is_superuser==True:
        num_publisher=User.objects.filter(is_publisher=True,is_active=False).count()
        data={'count': num_publisher}
        return JsonResponse(data)

    if request.user.is_publisher==True:
        num_request=BookNow.objects.filter(publisher=request.user,status='pending').count()
        data={'count': num_request}
        return JsonResponse(data)

    if request.user.is_customer==True:
        num_request=BookNow.objects.filter(customer=request.user,status='approved',pay_status='pending').count() + BookNow.objects.filter(customer=request.user,status='rejected').count()
        data={'count': num_request}
        return JsonResponse(data)

@login_required(login_url='/login/')
def newUpdate1(request):
    if request.user.is_customer==True:
        num_save=Save_Banner.objects.filter(cus=request.user).count()
        data1={'count1': num_save}
        return JsonResponse(data1)

@login_required(login_url='/login/')
def new_not1(request):
    if request.user.is_customer==True:
        new_save=Save_Banner.objects.filter(cus=request.user).values('cus__first_name','banner__publisher__first_name')
        print(new_save)
        return JsonResponse({'record': list(new_save)})

@login_required(login_url='/login/')
def newUpdate_rs(request):
    if request.user.is_publisher==True:
        pay=BookNow.objects.filter(publisher=request.user,pay_status='approved').count()
        data_rs={'count_rs': pay}
        return JsonResponse(data_rs)

@login_required(login_url='/login/')
def new_not_rs(request):
    if request.user.is_publisher==True:
        pay=BookNow.objects.filter(publisher=request.user,pay_status='approved').values('customer__first_name')
        return JsonResponse({'record': list(pay)})

#admin
@login_required(login_url='/login/')
def admin_publisher_list(request):
    data= User.objects.filter(is_publisher=True,is_active=True)
    return render(request, 'admin/admin_publisher_list.html',{'data':data})



@login_required(login_url='/login/')
def admin_delete_publisher(request,id):
    obj=User.objects.get(id=id)
    obj.delete()
    return  redirect(admin_publisher_list)

@login_required(login_url='/login/')
def admin_publisher_request(request):
    data= User.objects.filter(is_publisher=True,is_active=False)
    return render(request, 'admin/admin_publisher_request.html',{'data':data})

@login_required(login_url='/login/')
def admin_delete_publisher_request(request,id):
    obj=User.objects.get(id=id)
    obj.delete()
    return  redirect(admin_publisher_request)

@login_required(login_url='/login/')
def admin_publisher_request_accept(request,id):
    obj=User.objects.get(id=id)
    obj.is_active = True
    obj.save()
    return  redirect(admin_publisher_request)

@login_required(login_url='/login/')
def admin_order_banner(request):
    data = Order_Banner.objects.all()
    return render(request, 'admin/admin_order_banner.html', {'data': data})

@login_required(login_url='/login/')
def admin_booknow(request):
    data = BookNow.objects.all()
    return render(request, 'admin/admin_booknow.html', {'data': data})

@login_required(login_url='/login/')
def admin_mapdata(request):
    data = MapData.objects.all()
    return render(request, 'admin/admin_mapdata.html', {'data': data})

@login_required(login_url='/login/')
def admin_rating(request):
    data = Rating_Us.objects.all()
    return render(request, 'admin/admin_rating.html', {'data': data})

@login_required(login_url='/login/')
def admin_customer_list(request):
    data= User.objects.filter(is_customer=True,is_active=True)
    return render(request, 'admin/admin_customer_list.html',{'data':data})

@login_required(login_url='/login/')
def admin_delete_customer(request,id):
    obj=User.objects.get(id=id)
    obj.delete()
    return  redirect(admin_customer_list)

@login_required(login_url='/login/')
def admin_cus_pie_chart(request):
    labels = []
    data = []

    queryset = Rating_Us.objects.filter(rate_us__gte=1,cus__isnull=False)
    for city in queryset:
        labels.append(city.cus.first_name)
        data.append(city.rate_us)

    return render(request, 'admin/admin_cus_pie_chart.html', {
        'labels': labels,
        'data': data,
    })

@login_required(login_url='/login/')
def admin_pub_pie_chart(request):
    labels = []
    data = []

    queryset = Rating_Us.objects.filter(rate_us__gte=1,pub__isnull=False)
    for city in queryset:
        labels.append(city.pub.first_name)
        data.append(city.rate_us)

    return render(request, 'admin/admin_pub_pie_chart.html', {
        'labels': labels,
        'data': data,
    })

@login_required(login_url='/login/')
def pub_cus_pie_chart(request):
    labels = []
    data = []

    queryset = Rating_Us.objects.filter(pub=request.user,pub_rating__gte=1,)
    for city in queryset:
        labels.append(city.pub.first_name)
        data.append(city.pub_rating)

    return render(request, 'publisher/pub_cus_pie_chart.html', {
        'labels': labels,
        'data': data,
    })



# def location_search(request,id):
#     loc=location.objects.get(id=id)
#     data1 = location.objects.all()
#     data = MapData.objects.all()
#     return render(request, 'main_map.html', {'loc':loc,'data1':data1,'data':data})

# def profile_edit(request):
#     cus = request.user
#     form = CustomersForm(request.POST or None, initial={'first_name': cus.first_name,
#                                                       'last_name': cus.last_name})
#     if request.method == 'POST':
#         if form.is_valid():
#             cus.user.first_name = request.POST['first_name']
#             cus.user.last_name = request.POST['last_name']
#
#             cus.save()
#             return HttpResponseRedirect('index')
#
#     context = {
#         "form": form
#     }
#
#     return render(request, 'signin/profile_edit.html', context)
