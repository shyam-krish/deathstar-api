from django.contrib import admin
from .models import Artist, Album, Track, User, UserTrack

# Register your models here.
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(User)
admin.site.register(UserTrack)

