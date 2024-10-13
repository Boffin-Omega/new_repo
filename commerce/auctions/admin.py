from django.contrib import admin
from .models import auction_listing,comments,bids,User

# Register your models here.
admin.site.register(User)
admin.site.register(auction_listing)
admin.site.register(comments)
admin.site.register(bids)
