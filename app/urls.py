from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *
from django.contrib.auth import views as v

urlpatterns = [

    # homepage
    path('', views.homepage,name='home'),

    #login and registration
    path('login/', views.login_page, name='login_page'),
    path('enquiry/', views.enquiry, name='enquiry'),
    path('feedback/', views.feedback, name='feedback'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('cus_edit_profile/', views.cus_edit_profile, name='cus_edit_profile'),
    path('pub_edit_profile/', views.pub_edit_profile, name='pub_edit_profile'),
    path('change_password/',views.change_password,name='change_password'),
    path('password-reset/', v.PasswordResetView.as_view(template_name='signin/password_reset.html', email_template_name='signin/password_reset_email.html',subject_template_name='signin/password_reset_email_subject.txt'),name='password_reset'),
    path('password-reset-done/', v.PasswordResetDoneView.as_view(template_name='signin/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', v.PasswordResetConfirmView.as_view(template_name='signin/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', v.PasswordResetCompleteView.as_view(template_name='signin/password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', views.logout_user, name='logout'),
    path('pub_register/', views.pub_register, name='pub_register'),
    path('cus_register/', views.cus_register, name='cus_register'),

    #map
    path('surat_cus_map/', views.surat_cus_map,name='surat_cus_map'),
    path('bharuch_cus_map/', views.bharuch_cus_map,name='bharuch_cus_map'),
    path('surat_pub_map/', views.surat_pub_map,name='surat_pub_map'),
    path('bharuch_pub_map/', views.bharuch_pub_map, name='bharuch_pub_map'),
    path('surat_location_suggestion/', views.surat_location_suggestion, name='surat_location_suggestion'),
    path('bharuch_location_suggestion/', views.bharuch_location_suggestion, name='bharuch_location_suggestion'),

    # publisher
    path('add_marker/', views.add_marker, name='add_marker'),
    path('view_location/',views.view_location,name='view_location'),
    path('delete_location/<int:id>/',views.delete_location,name='delete_location'),
    path('edit_location/<int:id>/',views.edit_location,name='edit_location'),
    path('show_payment_done/', views.show_payment_done, name='show_payment_done'),
    path('update_mapdata/<int:id>/', views.update_mapdata, name='update_mapdata'),
    path('pub_cus_pie_chart/', views.pub_cus_pie_chart, name='pub_cus_pie_chart'),


    # booking
    path('booknow/<int:id>', views.booknow, name='booknow'),
    path('delete_booking/<int:id>/', views.delete_booking, name='delete_booking'),
    path('booking-request/',views.booking_request,name='booking_request'),
    path('booking-accept/<int:id>/',views.booking_accept,name='booking_accept'),
    path('booking-reject/<int:id>/',views.booking_reject,name='booking_reject'),
    path('show_my_booking/', views.show_my_booking, name='show_my_booking'),
    path('renew/<int:id>/', views.renew, name='renew'),

    #save for later
    path('save_banner/<int:id>', views.save_banner, name='save_banner'),
    path('show_save_banner/', views.show_save_banner, name='show_save_banner'),
    path('save_banner_map/', views.save_banner_map, name='save_banner_map'),
    path('delete_save_banner/<int:id>', views.delete_save_banner, name='delete_save_banner'),

    # notification
    path('newUpdate/',views.newUpdate,name='newUpdate'),
    path('newUpdate1/',views.newUpdate1,name='newUpdate1'),
    path('newUpdate_rs/', views.newUpdate_rs, name='newUpdate_rs'),
    path('new_not/', views.new_not, name='new_not'),
    path('new_not1/', views.new_not1, name='new_not1'),
    path('new_not_rs/', views.new_not_rs, name='new_not_rs'),

    #compare
    path('compare_surat/', views.compare_surat, name='compare_surat'),
    path('compare_bharuch/', views.compare_bharuch, name='compare_bharuch'),
    path('add_compare/<int:id>', views.add_compare, name='add_compare'),
    path('show_add_compare/', views.show_add_compare, name='show_add_compare'),
    path('delete_compare/<int:id>', views.delete_compare, name='delete_compare'),

    # paytm
    path('handlerequest/', views.handlerequest, name='handlerequest'),
    path('order/<int:id>', views.order, name='order'),

    #rating
    path('rating/', views.rating, name='rating'),
    path('pub_rating/', views.pub_rating, name='pub_rating'),

    #order
    path('order_banner/<int:id>', views.order_banner, name='order_banner'),
    path('show_order_banner/', views.show_order_banner, name='show_order_banner'),
    path('pay_order_banner/<int:id>/', views.pay_order_banner, name='pay_order_banner'),
    path('delete_order_banner/<int:id>', views.delete_order_banner, name='delete_order_banner'),

    #admin
    path('admin_publisher_list/', views.admin_publisher_list, name='admin_publisher_list'),
    path('admin_delete_publisher/<int:id>/', views.admin_delete_publisher, name='admin_delete_publisher'),
    path('admin_publisher_request/', views.admin_publisher_request, name='admin_publisher_request'),
    path('admin_delete_publisher_request/<int:id>/', views.admin_delete_publisher_request, name='admin_delete_publisher_request'),
    path('admin_publisher_request_accept/<int:id>/', views.admin_publisher_request_accept,name='admin_publisher_request_accept'),
    path('admin_customer_list/', views.admin_customer_list, name='admin_customer_list'),
    path('admin_delete_customer/<int:id>/', views.admin_delete_customer, name='admin_delete_customer'),
    path('admin_order_banner/', views.admin_order_banner, name='admin_order_banner'),
    path('admin_booknow/', views.admin_booknow, name='admin_booknow'),
    path('admin_mapdata/', views.admin_mapdata, name='admin_mapdata'),
    path('admin_rating/', views.admin_rating, name='admin_rating'),
    path('admin_cus_pie_chart/', views.admin_cus_pie_chart, name='admin_cus_pie_chart'),
    path('admin_pub_pie_chart/', views.admin_pub_pie_chart, name='admin_pub_pie_chart'),


]