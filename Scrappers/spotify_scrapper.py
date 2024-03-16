import spotipy
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

class SpotifyClient:
    def __init__(self):
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.CLIENT_ID,
                                                                        client_secret=self.CLIENT_SECRET))

    def get_song_information(self, track_id: str):
        return self.sp.track(track_id)

    def get_artist_id(self, artist_name: str):
        results = self.sp.search(q=artist_name, limit=1, type='artist')
        items = results['artists']['items']

        if len(items) > 0:
            return items[0]['id']

        return None

    def get_artist_albums(self, artist_name: str):
        artist_id = self.get_artist_id(artist_name)

        if artist_id:
            albums = self.sp.artist_albums(artist_id, album_type='album')
            albums['items'].reverse()

            return albums['items']

        return []

    def get_age_of_artist_when_album_was_released(self, artist_name: str, birtday: datetime, album_name: str):
        albums = self.get_artist_albums(artist_name)

        # Look for the album title in the list of albums
        filtered_list = list(filter(lambda x: x['name'] == album_name, albums))

        if filtered_list:
            release_date = datetime.strptime(filtered_list[0]['release_date'], "%Y-%m-%d")

            # Calculate the difference in years between new_date and birthday
            age = release_date.year - birtday.year

            # Adjust age if the birthday hasn't occurred yet in the current year
            if release_date.month < birtday.month or (release_date.month == birtday.month and release_date.day < birtday.day):
                age -= 1

            return age

        return None

    def get_average_days_between_releases(self, artist_name: str, album_name=None):
        albums = self.get_artist_albums(artist_name)

        if album_name:
            album_index = next((index for index, item in enumerate(albums) if item['name'] == album_name), None)

            # Check if album_index is found
            if album_index:
                # Consider albums after the specified album
                albums = albums[album_index:]

        # Calculate the difference in days between each album release
        days_between_releases = []

        # Check if the artist has more than one album
        # and that the release dates are not the same
        if len(albums) > 1:
            for i in range(1, len(albums)):
                release_date = datetime.strptime(albums[i]['release_date'], "%Y-%m-%d")
                previous_release_date = datetime.strptime(albums[i - 1]['release_date'], "%Y-%m-%d")

                if (release_date != previous_release_date):
                    days_between_releases.append((release_date - previous_release_date).days)

            # Factor in today's date in the average calculation
            today = datetime.now()
            days_since_last_release = (today - datetime.strptime(albums[-1]['release_date'], "%Y-%m-%d")).days
            days_between_releases.append(days_since_last_release)

            # Calculate the average days between releases
            average_days = sum(days_between_releases) / len(days_between_releases)
            return int(average_days)

        # If only one album was found, return days since the first album release
        if albums:
            release_date = datetime.strptime(albums[0]['release_date'], "%Y-%m-%d")
            today = datetime.now()
            return (today - release_date).days
        else:
            return None

    def find_most_streamed_song(self, songs, start_year, end_year):
        for song in songs:
            # Get the release year of the song
            song_information = self.get_song_information(song['Spotify Track Id'])
            release_date = datetime.strptime(song_information['album']['release_date'], "%Y-%m-%d")
            release_year = release_date.year

            if release_year and start_year <= release_year <= end_year and len(song_information['artists']) == 1:
                return song

        return None

# Example usage
if __name__ == "__main__":
    spotify_client = SpotifyClient()
    artist_name = "6ix9ine"

    average_days = spotify_client.get_average_days_between_releases(artist_name, "Dummy Boy")

    # age = spotify_client.get_age_of_artist_when_album_was_released(artist_name, "1991-02-17", "Plus")
    # average_days = spotify_client.get_average_days_between_releases()

