from django.urls import path

from . import views

urlpatterns = [
    path('artists/', views.ArtistList.as_view(), name='all-artists'),
    path('tracks/', views.TrackList.as_view(), name='all-tracks'),
    path('sync-with-spotify/', views.SyncDbWithSpotifyLikedSongs.as_view(), name='sync-db-with-spotify'),
    path('curate-playlist/', views.CuratePlaylist.as_view(), name='curate-playlist'),
    path('create-playlist/', views.CreateSpotifyPlaylist.as_view()),
    path('test/', views.Test.as_view(), name='test'),
]