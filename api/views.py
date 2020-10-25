import json
import os
import webbrowser
from pprint import pprint

import spotipy
import spotipy.util as util
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from spotipy.oauth2 import SpotifyOAuth

from .models import Artist, Album, Track, User, UserTrack
from .serializers import ArtistSerializer, AlbumSerializer, TrackSerializer, UserSerializer, UserTrackSerializer, \
    UrlSerializer

dev_url = 'http://127.0.0.1:8000'
prod_url = 'https://chopshop-api.herokuapp.com'


class UserList(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ArtistList(APIView):

    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

class AlbumList(APIView):

    def get(self, request):
        albums = Album.objects.all()
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)


class TrackList(APIView):

    def get(self, request):
        tracks = Track.objects.all()
        serializers = TrackSerializer(tracks, many=True)
        return Response(serializers.data)


class TrackForUser(APIView):

    def post(self, request):
        id = request.data.get('spotify_id')

        userTrack = UserTrack.objects.filter(user__spotify_id__contains=id)
        serializers = UserTrackSerializer(userTrack, many=True)

        return Response(serializers.data)


class SingleTrack(APIView):

    def post(self, request):
        id = request.data.get('spotify_id')

        print(id)

        track = Track.objects.filter(spotify_id=id)
        serializers = TrackSerializer(track, many=True)

        return Response(serializers.data)


class SpotifyUser(APIView):

    def post(self, request):
        caches_path = './.cache-123'
        scope = 'user-read-email'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        auth_manager.get_cached_token()

        print(auth_manager.get_authorize_url())
        print(auth_manager.client_id)
        print('here1')

        sp = spotipy.Spotify(auth_manager=auth_manager)
        print('here2')

        if sp:
            auth_url = auth_manager.get_authorize_url()
            print(auth_manager.get_authorize_url())

            try:
                print('here4')
                webbrowser.open(url=auth_url, new=1, autoraise=True)
                print('here5')
            except webbrowser.Error:
                return Response("Error opening browser", status=status.HTTP_400_BAD_REQUEST)

            user_result = sp.current_user()
            print('here3')

            json_response = json.dumps(user_result)
            pprint(json_response)

            print(user_result['display_name'])
        else:
            print("No token")

        return Response("User Printed", status=status.HTTP_200_OK)


class SyncDbWithSpotifyLikedSongs(APIView):

    def post(self, request):
        caches_path = './.cache123'
        scope = 'user-library-read, user-read-email'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        #auth_manager.get_cached_token()

        if os.path.exists(caches_path):
            print('file exists')

        sp = spotipy.Spotify(auth_manager=auth_manager)

        if sp:
            user_result = sp.current_user()

            # CREATE USER #
            user_spotify_id = user_result['id']
            user_name = user_result['display_name']
            user_email = user_result['email']

            user_db, created = User.objects.get_or_create(
                spotify_id=user_spotify_id,
                defaults={'name': user_name,
                          'email': user_email},
            )

            results = sp.current_user_saved_tracks(limit=50)
            json_response = json.dumps(results)
            pprint(json_response)

            offset = 0
            count = 50
            final_count = 0

            while count == 50:
                count = 0
                results = sp.current_user_saved_tracks(limit=50, offset=offset)

                for item in results['items']:
                    track = item['track']
                    count += 1
                    final_count += 1
                    print('Count: ' + count.__str__())
                    print('Final Count: ' + final_count.__str__())

                    try:
                        track_queryset = Track.objects.get(spotify_id=track['id'])
                    except Track.DoesNotExist:
                        track_queryset = None

                    if track_queryset:
                        try:
                            print('Getting User Track')
                            user_track = UserTrack.objects.get(user=user_db, track=track_queryset)
                        except UserTrack.DoesNotExist:
                            print('user track does not exist')
                            user_track = UserTrack(user=user_db, track=track_queryset)
                            user_track.save()

                    if track_queryset is None:
                        print('here1')

                        # CREATE ARTIST #
                        artist_spotify_id = track['artists'][0]['id']
                        artist = sp.artist(artist_spotify_id)
                        artist_name = artist['name']
                        artist_popularity = artist['popularity']
                        artist_followers_total = artist['followers']['total']

                        artist_db, created = Artist.objects.get_or_create(
                            spotify_id=artist_spotify_id,
                            defaults={'name': artist_name,
                                      'popularity': artist_popularity,
                                      'followers_total': artist_followers_total},
                        )

                        print('here2')

                        # CREATE ALBUM #
                        album_spotify_id = track['album']['id']
                        album = sp.album(album_spotify_id)
                        album_name = album['name']
                        album_popularity = album['popularity']
                        album_release_date = album['release_date']

                        album_db, created = Album.objects.get_or_create(
                            spotify_id=album_spotify_id,
                            defaults={'name': album_name,
                                      'artist': artist_db,
                                      'popularity': album_popularity},
                        )

                        print('here3')

                        # CREATE TRACK #
                        track_spotify_id = track['id']
                        track_title = track['name']
                        track_popularity = track['popularity']
                        track_duration_ms = track['duration_ms']

                        audio_features_list = sp.audio_features([track_spotify_id])
                        audio_features = audio_features_list[0]

                        track_key = audio_features['key']
                        track_mode = audio_features['mode']
                        track_time_signature = audio_features['time_signature']
                        track_acousticness = audio_features['acousticness']
                        track_danceability = audio_features['danceability']
                        track_energy = audio_features['energy']
                        track_instrumentalness = audio_features['instrumentalness']
                        track_liveness = audio_features['liveness']
                        track_loudness = audio_features['loudness']
                        track_speechiness = audio_features['speechiness']
                        track_valence = audio_features['valence']
                        track_tempo = audio_features['tempo']

                        track_db, created = Track.objects.get_or_create(
                            spotify_id=track_spotify_id,
                            defaults={'title': track_title,
                                      'popularity': track_popularity,
                                      'duration_ms': track_duration_ms,
                                      'artist': artist_db,
                                      'album': album_db,
                                      'key': track_key,
                                      'mode': track_mode,
                                      'time_signature': track_time_signature,
                                      'acousticness': track_acousticness,
                                      'danceability': track_danceability,
                                      'energy': track_energy,
                                      'instrumentalness': track_instrumentalness,
                                      'liveness': track_liveness,
                                      'loudness': track_loudness,
                                      'speechiness': track_speechiness,
                                      'valence': track_valence,
                                      'tempo': track_tempo},
                        )

                        print('here4')

                        # CREATE USER TRACK #
                        user_track = UserTrack.objects.create(user=user_db, track=track_db)
                        user_track.save()

                        print('here5')

                offset += 50
        else:
            print("No token")
            return Response("No token", status=status.HTTP_200_OK)

        if os.path.exists(caches_path):
            print('removing file')
            os.remove(caches_path)

        return Response("Added Songs", status=status.HTTP_200_OK)


class CuratePlaylist(APIView):

    def post(self, request):
        tempo_min = request.data.get('tempo_min', 0)
        tempo_max = request.data.get('tempo_max', 1000)
        artist_names = request.data.get('artists')

        playlist_name = request.data.get('playlist_name')
        playlist_description = request.data.get('playlist_description')
        public = request.data.get('public')

        print('artist names')
        print(artist_names)
        print('\n')


        if artist_names:
            curated_playlist = Track.objects.filter(artist__name__in=artist_names, tempo__range=(tempo_min, tempo_max)).values('spotify_id')
        else:
            curated_playlist = Track.objects.filter(tempo__range=(tempo_min, tempo_max)).values('spotify_id')

        spotify_ids = []
        for item in list(curated_playlist):
            spotify_id = item['spotify_id']
            spotify_ids.append(spotify_id)

        print('spotify_ids')
        print(spotify_ids)
        print('\n')

        caches_path = '/.cache-123'
        scope = 'user-library-read, playlist-read-collaborative, playlist-modify-public, playlist-read-private, playlist-modify-private'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        auth_manager.get_cached_token()

        sp = spotipy.Spotify(auth_manager=auth_manager)

        if sp:
            user_result = sp.current_user()

            user_spotify_id = user_result['id']

            is_public = True if public == 'True' else False

            sp.user_playlist_create(user_spotify_id, name=playlist_name, public=is_public, description=playlist_description)
            print('playlist created')
            print('\n')

            results = sp.user_playlists(user_spotify_id, limit=20)

            for item in results['items']:
                my_playlists_name = item['name']
                if my_playlists_name == playlist_name:
                    my_playlists_id = item['id']
                    sp.user_playlist_add_tracks(user_spotify_id, my_playlists_id, spotify_ids)

                    print(my_playlists_id)

        return Response("Playlist Curated and Created", status=status.HTTP_200_OK)


class CreateSpotifyPlaylist(APIView):

    def post(self, request):
        scope = 'user-library-read, playlist-read-collaborative, playlist-modify-public, playlist-read-private, playlist-modify-private'
        username = '1299958474'
        token = util.prompt_for_user_token(username, scope)

        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.user_playlists(username, limit=10)

            for item in results['items']:
                playlist_name = item['id']
                print(playlist_name)

            sp.user_playlist_create(username, name="Test Playlist", public=False, description="this is dope")
        return Response("created playlists", status=status.HTTP_200_OK)


class Redirect(APIView):

    def post(self, request):
        caches_path = './.cache-123'
        scope = 'user-read-email'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        url = {'url': auth_manager.get_authorize_url()}
        serializer = UrlSerializer(url)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Http(APIView):

    def get(self, request):
        return HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/api/v1/callback/')


class CallbackStaticRender(APIView):
    renderer_classes = [StaticHTMLRenderer]

    def get(self, request):
        caches_path = './.cache123'
        scope = 'user-library-read, user-read-email'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        code = self.request.query_params.get('code')
        if code:
            print('here1')
            auth_manager.get_access_token(code=code)
            return HttpResponseRedirect(redirect_to=prod_url + '/api/v1/callback/')

        if not auth_manager.get_cached_token():
            # Step 2. Display sign in link when no token
            print('here2')
            auth_url = auth_manager.get_authorize_url()
            print(auth_url)

            data = f'<h2><a href="{auth_url}">Sign in</a></h2>'
            return Response(data)

        print('here3')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user_result = spotify.current_user()

        display_name = user_result['display_name']
        client_url = 'https://chopshop-client.herokuapp.com/'

        data = '<html><body><h1>Hello ' + display_name + '. You are connected to Spotify :) </h1>'
        data += f'<h2><a href="{client_url}">Now click here!</a></h2>'
        data += '</body></html>'
        
        return Response(data)
