from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,auction_listing,comments,bids, listing_form
import json
import datetime

c_L =  ["Books","Clothing", "Shoes & Jewelry", "Home & Kitchen", "Beauty & Personal Care","Health & Household",
"Toys & Games","Sports & Outdoors","Automotive","Industrial & Scientific","Food","Electronic appliances","Accessories"]
categories = [(item, item) for item in c_L]
def index(request):
    items = auction_listing.objects.all()
    return render(request, "auctions/index.html",{
        "items":items,
        "categories":c_L
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request,id):
    if request.method == "POST":
        #adding a comment
        date= str(datetime.datetime.now()).split()[0]
        comment = request.POST.get("comment")
        user= User.objects.get(pk=request.user.id)
        new_comment = comments(item_id = id, user_id = user, comment = comment, date=date)
        new_comment.save()

    #to check if given listing is in users watchlist
    watchlist = request.user.watchlist
    if watchlist == '':
        wl=None
    else:
        wl=watchlist.split(",")

    item = auction_listing.objects.get(pk=id)
    bid = bids.objects.get(item_id = item.id) # gets the latest bid(highest price) bid of the given item
    return render(request,"auctions/listing.html",{
        "name":item.name,
        "price": item.price,
        "category": item.category,
        "description": item.description,
        "img": item.img,
        "id":str(item.id),
        "comments":comments.objects.filter(item_id = item.id).select_related(),
        "watchlist":wl,
        "bid":bid
    })

def bid(request):
    watchlist = request.user.watchlist
    if watchlist == '':
        wl=None
    else:
        wl=watchlist.split(",")

    if request.method == "GET":

        #going to this route only if user places a bid on an unsold item
        buyer_id = request.GET.get("buyer_id")
        item_id = request.GET.get("id")
        price = (request.GET.get("bid"))

        

        bid = bids.objects.get(item_id = item_id)
        item = auction_listing.objects.get(pk=item_id)
        #Entered bid price must be greater than current bid price

        if type(price)!= int:
            msg="Please enter a valid bid amount!"
        elif price < bid.bid_price:
            msg = "Must bid higher than current highest bid!"
        else:
            msg=''
            #update query for given bid and save it, return to same listing page again
            bid.bid_price = price
            bid.buyer_id = buyer_id
            bid.save(update_fields=["bid_price","buyer_id"]) #only updates these 2 fields
        
        return render(request,"auctions/listing.html",{
            "name":item.name,
            "price": item.price,
            "category": item.category,
            "description": item.description,
            "img": item.img,
            "id":str(item.id),
            "comments":comments.objects.filter(item_id = item.id).select_related(),
            "watchlist":wl,
            "bid":bid,
            "msg":msg
            })
    else:
        #post request means owner wants to close the auction
        item_id = request.POST.get("id")
        bid = request.POST.get("bid")
        bid = bids.objects.get(item_id=item_id)
        bid.status = "Sold"
        bid.save()
        return HttpResponseRedirect(reverse("listing",args=[item_id]))

def watchlist(request):
    user = request.user
    if request.method == "GET":
        # either its a request to render the watchlist page or add new item to watchlist
        id = request.GET.get("id") #get item id , if the "add to watchlist" button was clicked else return none

        if id != None:
            # request to add new item to watchlist
            #2 cases, one where i add to an empty list and when i add to a non empty list
            watchlist = user.watchlist
            if watchlist == '':
                # adding to an empty watchlist
                watchlist = [id]
            else:
                # adding to a non empty watchlist
                watchlist = watchlist.split(",")
                watchlist.append(id)
            user.watchlist = ",".join(watchlist)
            user.save()
            return HttpResponseRedirect(reverse("watchlist"))
        else: 
            # request to render user's watchlist page
            watchlist = user.watchlist
            if watchlist != '':
                #non empty watchlist
                watchlist = watchlist.split(",")
                w_items = auction_listing.objects.filter(id__in=watchlist) # equivalent of SELECT * FROM auction_listing WHERE id IN watchlist;
            else:
                w_items = None
            return render(request,"auctions/watchlist.html",{
                "w_items":w_items
            })
    else:
        #post request
        #meaning user wants to remove certain item from their watchlist
        watchlist = user.watchlist.split(",")
        item_id = request.POST.get("item_id")
        watchlist.remove(item_id) 
        user.watchlist = ",".join(watchlist)
        user.save()
        return HttpResponseRedirect(reverse("watchlist"))

def create(request):
    if request.method == "POST":
        #add new listing
        form = listing_form(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            category = form.cleaned_data["category"]
            desc = form.cleaned_data["description"]
            img = form.cleaned_data["img"]
            price = form.cleaned_data["price"]

            item = auction_listing(name = name, price = price, category = category, description = desc, img = img )
            item.save()

            owner_id = User.objects.get(pk=request.user.id).id
            bid_record = bids(owner_id=owner_id, bid_price=price, item_id=item.id) #no buyer_id for new listings, im creating this bid record here itself instead of when bid button is clicked
            #cuz if i didnt i wouldnt have any way of storing/getting to know owner_id.
            
            bid_record.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(reverse("create"))
    else:
        form = listing_form()
        return render(request,"auctions/create.html",{
            "form":form
        })

def category(request):
    category = request.GET.get("category")
    items = auction_listing.objects.filter(category=category)
    print(items)

    return render(request, "auctions/index.html",{
        "items":items
    })

