from django import forms
from django.core.exceptions import ValidationError

from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import DateTimeField
import datetime

class DateForm(forms.Form):
    date = forms.DateTimeField(input_formats=['%Y/%m/%d '])

class DateInput(forms.DateInput):
    input_type = 'date'

class PublishersForm(UserCreationForm):
    username = forms.EmailField(label='Email-id',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Email'}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'placeholder': 'Password Should be character+number+symbol lenght(8-13)'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Please Re-Enter Password'}))
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Please Enter First Name'}),required=True)
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Last Name'}))
    phone = forms.IntegerField(label='Mobile Number',widget=forms.TextInput(attrs={'placeholder': 'Please Enter 10 digit Mobile number'}))

    class Meta:
        model=get_user_model()
        fields=('first_name','last_name','username','password1','password2','phone','address','city','logo',)

class CustomersForm(UserCreationForm):
    username=forms.EmailField(label='Email-id',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Email'}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'placeholder': 'Password Should be character+number+symbol lenght(8-13)'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Please Re-Enter Password'}))
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter First Name'}))
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Last Name'}))
    phone = forms.IntegerField(label='Mobile Number',widget=forms.TextInput(attrs={'placeholder': 'Please Enter 10 digit Mobile number'}),validators=[RegexValidator(regex='\d{10}',message='invalid number',code='invalid_number')])

    class Meta:
        model=get_user_model()
        fields=('first_name','last_name','username','password1','password2','phone','address',)



class MapDataForm(forms.ModelForm):
    height = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Please Enter input in feet'}))
    width = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Please Enter input in feet'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Please Enter input in Rs'}))

    class Meta:
        model=MapData
        fields='__all__'
        exclude=('publisher',)
        widgets = {
            "latitude": forms.TextInput(attrs={'placeholder': 'Latitude', 'id': 'latitude',}),
            "longitude": forms.TextInput(attrs={'placeholder': 'Longitude', 'id': 'longitude',}),
            'to_date': DateInput()
        }

class BookNowForm(forms.ModelForm):

    class Meta:
        model=BookNow
        fields='__all__'
        exclude=('status','customer','publisher','mapdata','days','pay_status')
        widgets = {'from_date': DateInput(),'to_date': DateInput()}

class SaveBannerForm(forms.ModelForm):
    class Meta:
        model=Save_Banner
        fields=[]

class OrderBannerForm(forms.ModelForm):
    class Meta:
        model=Order_Banner
        fields=[]
            # ('unid',)

class CompareBannerForm(forms.ModelForm):
    class Meta:
        model=Compare_Banner
        fields=[]

class RatingForm(forms.ModelForm):
    class Meta:
        model=Rating_Us
        fields=[]

class PubRatingForm(forms.ModelForm):
    class Meta:
        model=Rating_Us
        fields=[]


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


# class UpdateProfile(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name','phone','address',)
#
#     def clean_email(self):
#         username = self.cleaned_data.get('username')
#         email = self.cleaned_data.get('username')
#
#         if email and User.objects.filter(email=email).exclude(username=username).count():
#             raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
#         return email
#
#     def save(self, commit=True):
#         user = super(CustomersForm, self)
#         user.email = self.cleaned_data['email']
#
#         if commit:
#             user.save()
#
#         return user

class CusEditProfile(forms.ModelForm):
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter First Name'}),required=False)
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Last Name'}),required=False)
    phone = forms.IntegerField(label='Mobile Number',widget=forms.TextInput(attrs={'placeholder': 'Please Enter 10 digit Mobile number'}),required=False)
    address = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'placeholder': 'Please Enter Address'}),required=False)
    class Meta:
        model = User
        fields = ('first_name', 'last_name','address', 'phone')


class PubEditProfile(forms.ModelForm):
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter First Name'}),required=False)
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder': 'Please Enter Last Name'}),required=False)
    phone = forms.IntegerField(label='Mobile Number',widget=forms.TextInput(attrs={'placeholder': 'Please Enter 10 digit Mobile number'}),required=False)
    address = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'placeholder': 'Please Enter Address'}),required=False)
    class Meta:
        model = User
        fields = ('first_name', 'last_name','address', 'phone','city','logo')

class UserDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []
