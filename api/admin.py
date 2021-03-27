from django.contrib import admin
from .models import Artist, Album, Track, User, UserTrack, Song, UserSong

# Register your models here.
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(User)
admin.site.register(UserTrack)
admin.site.register(Song)
admin.site.register(UserSong)
