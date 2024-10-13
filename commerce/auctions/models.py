from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.core.validators import MinValueValidator

c_L =  ["Books","Clothing", "Shoes & Jewelry", "Home & Kitchen", "Beauty & Personal Care","Health & Household",
"Toys & Games","Sports & Outdoors","Automotive","Industrial & Scientific","Food","Electronic appliances","Accessories"]

categories = [(item, item) for item in c_L]

class listing_form(forms.Form):
    name = forms.CharField(max_length = 64, label="Product Name", error_messages = { 
                 'required':"Please Enter a valid product name"
                 })
    price = forms.FloatField(label="Starting Bid", error_messages ={
        'required':"Please enter a valid starting bid price"
    })
    category = forms.ChoiceField(label="Category", choices=categories,error_messages ={
        'required':'Please choose a valid category'
    })
    description = forms.CharField(max_length = 300, label="Product Description",widget=forms.Textarea)
    img = forms.ImageField( required=False,label="Upload Images(if any)")
class User(AbstractUser):
    watchlist = models.TextField(default='')

class auction_listing(models.Model):
    #model for storing each item of auction listing
    # im thinking each item could have a name, price, category, sold/unsold, stock left, img url
    name = models.CharField(max_length = 64)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    category = models.CharField(max_length = 64)
    description = models.CharField(max_length = 300, default='No description provided by seller')
    img = models.ImageField(null=True,blank=True)

    class Meta():
        #without this apparently it doesnt show properly on the admin page
        verbose_name_plural = "listings"
    def __str__(self):
        return self.img.name

class comments(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
    user_id = models.ForeignKey("User",on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.CharField(max_length=10, default='')

class bids(models.Model):
    bid_id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField(null=True)
    item_id = models.IntegerField(default=-1)
    buyer_id = models.IntegerField(null=True)
    bid_price = models.FloatField(null=True, validators=[MinValueValidator(0.0)])
    status = models.CharField(default="Unsold",max_length=6)

