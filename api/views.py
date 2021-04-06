import os
import uuid

import spotipy
import spotipy.util as util
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from spotipy.oauth2 import SpotifyOAuth

from datetime import datetime


from .serializers import ArtistSerializer, AlbumSerializer, TrackSerializer, UserSerializer, UrlSerializer, \
    UserTrackTrackSerializer
from .utils import *

dev_url = 'http://127.0.0.1:8080'
prod_url = 'http://ec2-18-206-163-235.compute-1.amazonaws.com'

spotify_cache_folder = './.spotify_cache/'

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

        user_track = UserTrack.objects.filter(user__spotify_id__contains=id)
        serializers = UserTrackTrackSerializer(user_track, many=True)

        return Response(serializers.data)


class SingleTrack(APIView):

    def post(self, request):
        id = request.data.get('spotify_id')

        print(id)

        track = Track.objects.filter(spotify_id=id)
        serializers = TrackSerializer(track, many=True)

        return Response(serializers.data)

class SyncDbWithSpotifyLikedSongs(APIView):

    def post(self, request):
        caches_path = './.cache123'
        scope = 'user-library-read, user-read-email, user-top-read'

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

            user, created = User.objects.get_or_create(
                spotify_id=user_spotify_id,
                defaults={'name': user_name,
                          'email': user_email},
            )

            # results = sp.current_user_saved_tracks(limit=50)
            # json_response = json.dumps(results)
            # pprint(json_response)
            #
            # offset = 0
            # count = 50
            final_count = 0

            count = 0

            #while count == 50 and offset < 350:
            while count < 21:
               #results = sp.current_user_saved_tracks(limit=50, offset=offset)
                results = sp.current_user_top_tracks(time_range="short_term")

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
                            user_track = UserTrack.objects.get(user=user, track=track_queryset)
                        except UserTrack.DoesNotExist:
                            print('user track does not exist')
                            user_track = UserTrack(user=user, track=track_queryset)
                            user_track.save()

                    if track_queryset is None:
                        print('here1')

                        artist = create_artist(track, sp)
                        album = create_album(track, artist, sp)
                        track = create_track(track, artist, album, sp)
                        create_user_track(user, track)

                        print('here2')

                #offset += 50
        else:
            print("No token")
            return Response("No token", status=status.HTTP_200_OK)

        if os.path.exists(caches_path):
            print('removing file')
            os.remove(caches_path)

        return Response("Added Songs", status=status.HTTP_200_OK)


class SyncSpotifyUserTopTracks(APIView):

    def post(self, request):
        caches_path = './.cache123'
        scope = 'user-read-email, user-top-read'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=caches_path,
                                    show_dialog=True)

        if os.path.exists(caches_path):
            print('file exists')

        sp = spotipy.Spotify(auth_manager=auth_manager)

        if sp:
            user = create_spotify_user(spotipy=sp)

            results = sp.current_user_top_tracks(limit=10, time_range="short_term")
            print(results)

            for item in results['items']:
                try:
                    track_from_db = Track.objects.get(spotify_id=item['id'])
                except Track.DoesNotExist:
                    track_from_db = None

                if track_from_db:
                    try:
                        print('Getting UserTrack')
                        user_track = UserTrack.objects.get(user=user, track=track_from_db)
                    except UserTrack.DoesNotExist:
                        print('UserTrack does not exist')
                        create_user_track(user=user, track=track_from_db)

                else:
                    print('here1')

                    artist = create_artist(artist_id=item['artists'][0]['id'], spotipy=sp)
                    album = create_album(album_id=item['album']['id'], artist=artist, spotipy=sp)
                    created_track = create_track(track=item, artist=artist, album=album, spotipy=sp)
                    create_user_track(user=user, track=created_track)

                    print('here2')

        else:
            print("No token")
            return Response("No token", status=status.HTTP_200_OK)

        if os.path.exists(caches_path):
            print('removing file')
            os.remove(caches_path)

        return Response("Added Top Songs For User", status=status.HTTP_200_OK)


class SyncSpotifyUserTopSongs(APIView):

    def post(self, request):

        try:
            print('Getting cache id from session..')
            print(request.session['cache_id'])
            cache = request.session['cache_id']
        except KeyError:
            print('Could not get cache')
            return Response('Could not get cache', status=status.HTTP_400_BAD_REQUEST)
            # return Response("No Cache", status=status.HTTP_200_OK)

        cache_path = spotify_cache_folder + cache

        if os.path.exists(cache_path):
            print('file exists')

        scope = 'user-read-email, user-top-read'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=cache_path,
                                    show_dialog=True)

        sp = spotipy.Spotify(auth_manager=auth_manager)

        if sp:
            user = create_spotify_user(spotipy=sp)

            results = sp.current_user_top_tracks(limit=10, time_range="short_term")

            print(results)

            for item in results['items']:
                song = None

                try:
                    song = Song.objects.get(spotify_id=item['id'])
                except Song.DoesNotExist:
                    pass

                try:
                    song = Song.objects.get(title=item['name'])
                except Song.DoesNotExist:
                    pass

                if song is None:
                    print('Song does not exist in db')

                    artist = create_artist(artist_id=item['artists'][0]['id'], spotipy=sp)
                    album = create_album(album_id=item['album']['id'], artist=artist, spotipy=sp)
                    song = create_song(track=item, artist=artist, album=album, spotipy=sp)

                    print('Persisted artist, album and song')

                create_user_song(user, song)

        else:
            print("No token")
            return Response("No token", status=status.HTTP_200_OK)

        return Response("Added Top Songs For User", status=status.HTTP_200_OK)


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

class CallbackStaticRender(APIView):
    renderer_classes = [StaticHTMLRenderer]

    def get(self, request):
        new_cache = str(uuid.uuid4())

        cache = request.session.get('cache_id', new_cache)

        cache_path = spotify_cache_folder + cache
        print('cache_path:' + cache_path)

        scope = 'user-read-email, user-top-read'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=cache_path,
                                    show_dialog=True)

        code = self.request.query_params.get('code')
        if code:
            print('code: ' + code)
            auth_manager.get_access_token(code=code)
            print('redirecting..')
            return HttpResponseRedirect(redirect_to='http://localhost:8080/index3.html')

        if not auth_manager.get_cached_token():
            auth_url = auth_manager.get_authorize_url()

            data = f'<h2><a href="{auth_url}">Sign in</a></h2>'
            return Response(data)

        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user_result = spotify.current_user()

        display_name = user_result['display_name']
        client_url = 'https://chopshop-client.herokuapp.com/'

        data = '<html><body><h1>Hello ' + display_name + '. You are connected to Spotify :) </h1>'
        data += f'<h2><a href="{client_url}">Now click here!</a></h2>'
        data += '</body></html>'
        
        return Response(data)


class Callback(APIView):

    def get(self, request):
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        new_cache = str(uuid.uuid4())
        print('New UUID: ' + new_cache)

        try:
            cache = request.session['cache_id']
            print('cache exists')
        except KeyError:
            print('new cache')
            request.session['cache_id'] = new_cache
            cache = request.session['cache_id']

        cache_path = spotify_cache_folder + cache
        print('cache_path: ' + cache_path)

        if os.path.exists(cache_path):
            print('cache file exists')
        else:
            print('cache file does not exist')

        scope = 'user-read-email, user-top-read'

        auth_manager = SpotifyOAuth(scope=scope,
                                    cache_path=cache_path,
                                    show_dialog=True)

        code = self.request.query_params.get('code')
        print(code)
        if code:
            print('code: ' + code)
            auth_manager.get_access_token(code=code)
            print('redirecting..')
            redirect_url = dev_url + '/success.html'
            return HttpResponseRedirect(redirect_to=redirect_url)

        if not auth_manager.get_cached_token():
            url = {'url': auth_manager.get_authorize_url()}
            serializer = UrlSerializer(url)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            url = {'url': auth_manager.get_authorize_url()}
            serializer = UrlSerializer(url)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response("ERROR", status=status.HTTP_400_BAD_REQUEST)


class Session(APIView):

    def get(self, request):
        # print('\n-------------')
        # print('Printing session:')
        # visits = request.session.get('num_visits', 1)
        # request.session['num_visits'] = visits + 1
        # print(visits)
        #
        # new_cache = str(uuid.uuid4())
        # try:
        #     cache = request.session['cache_id']
        #     print('cache exists')
        # except KeyError:
        #     print('new cache')
        #     request.session['cache_id'] = new_cache
        #     cache = request.session['cache_id']
        #
        # print(cache)
        # print('-------------\n')

        request.session.flush()
        print('cache flushed')

        return Response("printed", status=status.HTTP_200_OK)