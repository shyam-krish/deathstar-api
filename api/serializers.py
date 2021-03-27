from rest_framework import serializers
from .models import Artist, Album, Track, User, UserTrack, Song, UserSong


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'spotify_id', 'name', 'phone', 'email', 'user_type', 'followers_total')


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
        fields = ('id', 'title', 'artist', 'popularity', 'spotify_id', 'popularity', 'album', 'duration_ms',
                  'key', 'mode', 'time_signature', 'acousticness', 'danceability', 'energy',
                  'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo')


class UserTrackSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    track = TrackSerializer()

    class Meta:
        model = UserTrack
        fields = ('user', 'track')


class UserTrackTrackSerializer(serializers.Serializer):
    track = TrackSerializer()

    class Meta:
        model = UserTrack
        fields = ('track.title')


class UrlSerializer(serializers.Serializer):
    url = serializers.CharField()


class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    album = AlbumSerializer()

    class Meta:
        model = Song
        fields = ('title', 'artist', 'album', 'filepath', 'spotify_id', 'billboard', 'year', 'duration_ms', 'bpm')


class UserSongSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    song = SongSerializer()

    class Meta:
        model = UserSong
        fields = ('user', 'song')


