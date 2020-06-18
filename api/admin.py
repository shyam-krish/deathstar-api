from django.contrib import admin
from .models import Artist, Album, Track, Genre

# Register your models here.
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(Genre)
