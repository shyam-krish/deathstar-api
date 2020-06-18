from rest_framework import serializers
from .models import Artist, Album, Track, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

class ArtistSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()

    class Meta:
        model = Artist
        fields = ('id', 'spotify_id', 'name', 'popularity', 'followers_total', 'genre')


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    genre = GenreSerializer()
    release_date = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])

    class Meta:
        model = Album
        fields = ('id', 'spotify_id', 'name', 'artist', 'popularity', 'release_date', 'genre')


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    album = AlbumSerializer()
    genre = GenreSerializer()

    class Meta:
        model = Track
        fields = ('id', 'artist', 'popularity', 'spotify_id', 'popularity', 'album', 'duration_ms',
                  'genre', 'key', 'mode', 'time_signature', 'acousticness', 'danceability', 'energy',
                  'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo')



