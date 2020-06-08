from rest_framework import serializers
from .models import Artist, Album, Track


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'spotify_id', 'name', 'popularity', 'followers_total')

class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    release_date = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])

    class Meta:
        model = Album
        fields = ('id', 'spotify_id', 'name', 'artist', 'popularity', 'release_date')


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    album = AlbumSerializer()

    class Meta:
        model = Track
        fields = ('id', 'artist', 'popularity', 'spotify_id', 'popularity', 'album', 'duration_ms',
                  'key', 'mode', 'time_signature', 'acousticness', 'danceability', 'energy',
                  'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo')
