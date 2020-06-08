from django.shortcuts import render

from .models import Artist, Album, Track
from .serializers import ArtistSerializer, TrackSerializer

from rest_framework import generics

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

import spotipy
import spotipy.util as util
import json
from pprint import pprint

class ArtistList(APIView):

    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

class TrackList(APIView):

    def get(self, request):
        tracks = Track.objects.all()
        serializers = TrackSerializer(tracks, many=True)
        return Response(serializers.data)


class Test(APIView):

    def get(self, request):
        try:
            track = Track.objects.get(spotify_id=10)
            print('hi')
        except Track.DoesNotExist:
            track = None
            print('bye')

        serializer = TrackSerializer(track)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        spotify_id = '3'
        name = 'Shyam'
        popularity = '100'
        followers_total = '1000'

        obj, created = Artist.objects.get_or_create(
            spotify_id=spotify_id,
            defaults={'name': name,
                      'popularity': popularity,
                      'followers_total': followers_total},
        )

        print(obj)

        if created:
            return Response(obj, status=status.HTTP_201_CREATED)
        else:
            return Response("Already an Artist", status=status.HTTP_400_BAD_REQUEST)


class SyncDbWithSpotifyLikedSongs(APIView):

    def post(self, request):
        scope = 'user-library-read'
        username = '1299958474'
        token = util.prompt_for_user_token(username, scope)

        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.current_user_saved_tracks(limit=50)
            json_response = json.dumps(results)
            pprint(json_response)
            for item in results['items']:
                track = item['track']
                # json_response = json.dumps(track)
                # pprint(json_response)
                print('first')

                try:
                    track_queryset = Track.objects.get(spotify_id=track['id'])
                except Track.DoesNotExist:
                    track_queryset = None

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

                    # if track['album']['album_type'] != 'single':
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

                    print(track_title)
                    print(track_popularity)
                    print(track_duration_ms)

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
                    # print(audio_features)
                    # print(track['name'] + ' - ' + track['artists'][0]['name'])

        else:
            print("Can't get token for", username)

        return Response("Added Songs", status=status.HTTP_200_OK)

    def get(self, response):
        scope = 'user-library-read'
        username = '1299958474'
        token = util.prompt_for_user_token(username, scope)

        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.current_user_saved_tracks(limit=1)
            # json_response = json.dumps(results)
            # pprint(json_response)
            for item in results['items']:
                track = item['track']

                track_name = track['name']
                print(track_name)

                track_spotify_id = track['id']
                audio_features = sp.audio_features([track_spotify_id])

                track_key = audio_features[0]['key']
                print(track_key)

                return Response(audio_features, status=status.HTTP_200_OK)

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

        scope = 'user-library-read, playlist-read-collaborative, playlist-modify-public, playlist-read-private, playlist-modify-private'
        username = '1299958474'
        token = util.prompt_for_user_token(username, scope)

        if token:
            sp = spotipy.Spotify(auth=token)

            is_public = True if public == 'True' else False

            sp.user_playlist_create(username, name=playlist_name, public=is_public, description=playlist_description)
            print('playlist created')
            print('\n')

            results = sp.user_playlists(username, limit=20)

            for item in results['items']:
                my_playlists_name = item['name']
                if my_playlists_name == playlist_name:
                    my_playlists_id = item['id']
                    sp.user_playlist_add_tracks(username, my_playlists_id, spotify_ids)

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









