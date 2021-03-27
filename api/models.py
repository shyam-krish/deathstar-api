from django.db import models

class User(models.Model):

    USER_TYPES = [
        ('DJ', 'DJ'),
        ('SUPERFAN', 'Superfan'),
        ('FAN', 'Fan'),
    ]

    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    user_type = models.CharField(max_length=255, choices=USER_TYPES, default='FAN')
    followers_total = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.spotify_id + ' - ' + self.name


class Artist(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    followers_total = models.IntegerField(null=True, blank=True)
    insta_followers = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name + " - " + self.artist.name


class Track(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    popularity = models.CharField(max_length=255, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    #Audio Features
    key = models.IntegerField(null=True, blank=True)
    mode = models.IntegerField(null=True, blank=True)
    time_signature = models.IntegerField(null=True, blank=True)
    acousticness = models.FloatField(blank=True, null=True)
    danceability = models.FloatField(blank=True, null=True)
    energy = models.FloatField(blank=True, null=True)
    instrumentalness = models.FloatField(blank=True, null=True)
    liveness = models.FloatField(blank=True, null=True)
    loudness = models.FloatField(blank=True, null=True)
    speechiness = models.FloatField(blank=True, null=True)
    valence = models.FloatField(blank=True, null=True)
    tempo = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title + " - " + self.artist.name


class UserTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + " - " + self.track.title

class Song(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    filepath = models.CharField(max_length=255, null=True, blank=True)
    spotify_id = models.CharField(max_length=255, null=True, blank=True)
    billboard = models.BooleanField(default=False)
    year = models.CharField(max_length=4, null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    bpm = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title + " - " + self.artist.name

class UserSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + " - " + self.song.title




