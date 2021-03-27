from .models import Artist, Album, Track, User, UserTrack


def create_spotify_user(spotipy):
    user_result = spotipy.current_user()

    # CREATE USER #
    user_spotify_id = user_result['id']
    user_name = user_result['display_name']
    user_email = user_result['email']

    user, created = User.objects.get_or_create(
        spotify_id=user_spotify_id,
        defaults={'name': user_name,
                  'email': user_email},
    )

    return user

def create_artist(artist_id, spotipy):
    artist = spotipy.artist(artist_id)
    artist_name = artist['name']
    artist_popularity = artist['popularity']
    artist_followers_total = artist['followers']['total']

    artist, created = Artist.objects.get_or_create(
        spotify_id=artist_id,
        defaults={'name': artist_name,
                  'popularity': artist_popularity,
                  'followers_total': artist_followers_total},
    )

    return artist

def create_album(album_id, artist, spotipy):
    album = spotipy.album(album_id)
    album_name = album['name']
    album_popularity = album['popularity']

    album, created = Album.objects.get_or_create(
        spotify_id=album_id,
        defaults={'name': album_name,
                  'artist': artist,
                  'popularity': album_popularity},
    )

    return album

def create_track(track, artist, album, spotipy):
    track_spotify_id = track['id']
    track_title = track['name']
    track_popularity = track['popularity']
    track_duration_ms = track['duration_ms']

    print(track_title)

    audio_features_list = spotipy.audio_features([track_spotify_id])
    audio_features = audio_features_list[0]

    track, created = Track.objects.get_or_create(
        spotify_id=track_spotify_id,
        defaults={'title': track_title,
                  'popularity': track_popularity,
                  'duration_ms': track_duration_ms,
                  'artist': artist,
                  'album': album,
                  'key': audio_features['key'],
                  'mode': audio_features['mode'],
                  'time_signature': audio_features['time_signature'],
                  'acousticness': audio_features['acousticness'],
                  'danceability': audio_features['danceability'],
                  'energy': audio_features['energy'],
                  'instrumentalness': audio_features['instrumentalness'],
                  'liveness': audio_features['liveness'],
                  'loudness': audio_features['loudness'],
                  'speechiness': audio_features['speechiness'],
                  'valence': audio_features['valence'],
                  'tempo': audio_features['tempo']},
    )

    return track

def create_user_track(user, track):
    user_track = UserTrack.objects.create(user=user, track=track)
    user_track.save()

    return user_track



