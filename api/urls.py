from django.urls import path

from . import views

urlpatterns = [
    path('sync-spotify-top-songs/', views.SyncSpotifyUserTopSongs.as_view(),
         name='sync-spotify-top-songs'),
    path('callback2/', views.Callback.as_view()),
]