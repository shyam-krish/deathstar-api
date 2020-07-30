from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UserList.as_view(), name='all-users'),
    path('artists/', views.ArtistList.as_view(), name='all-artists'),
    path('albums/', views.AlbumList.as_view(), name='all-albums'),
    path('tracks/', views.TrackList.as_view(), name='all-tracks'),
    path('track-for-user/', views.TrackForUser.as_view(), name='track-for-user'),
    path('single-track/', views.SingleTrack.as_view(), name='single-track'),
    path('spotify-user/', views.SpotifyUser.as_view(), name='spotify-user'),
    path('sync-with-spotify/', views.SyncDbWithSpotifyLikedSongs.as_view(), name='sync-db-with-spotify'),
    path('curate-playlist/', views.CuratePlaylist.as_view(), name='curate-playlist'),
    path('create-playlist/', views.CreateSpotifyPlaylist.as_view()),
    path('test/', views.Test.as_view(), name='test'),
]