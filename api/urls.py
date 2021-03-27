from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UserList.as_view(), name='all-users'),
    path('artists/', views.ArtistList.as_view(), name='all-artists'),
    path('albums/', views.AlbumList.as_view(), name='all-albums'),
    path('tracks/', views.TrackList.as_view(), name='all-tracks'),
    path('track-for-user/', views.TrackForUser.as_view(), name='track-for-user'),
    path('single-track/', views.SingleTrack.as_view(), name='single-track'),
    path('sync-with-spotify/', views.SyncDbWithSpotifyLikedSongs.as_view(), name='sync-with-spotify'),
    path('sync-spotify-top-tracks/', views.SyncSpotifyUserTopTracks.as_view(),
         name='sync-spotify-top-tracks'),
    path('sync-spotify-top-songs/', views.SyncSpotifyUserTopSongs.as_view(),
         name='sync-spotify-top-songs'),
    path('curate-playlist/', views.CuratePlaylist.as_view(), name='curate-playlist'),
    path('create-playlist/', views.CreateSpotifyPlaylist.as_view()),
    path('redirect/', views.Redirect.as_view()),
    path('http-redirect/', views.Http.as_view()),
    path('callback/', views.CallbackStaticRender.as_view()),
]