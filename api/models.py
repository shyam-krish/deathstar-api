from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    followers_total = models.IntegerField(null=True, blank=True)
    insta_followers = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.name + " - " + self.artist.name


class Track(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    popularity = models.CharField(max_length=255, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)

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

