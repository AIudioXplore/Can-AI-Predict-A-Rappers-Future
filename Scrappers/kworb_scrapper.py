from bs4 import BeautifulSoup
import requests
from Scrappers.spotify_scrapper import SpotifyClient

class KworbScrapper:
    def __init__(self):
        pass

    def find_artist(self, artist_name):
        # Send a GET request to the webpage
        response = requests.get("https://kworb.net/spotify/listeners.html")

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <a> element containing artist name
        artist_element = soup.find('a', text=artist_name)

        if artist_element:
            # Extract the link from the element
            link = "https://kworb.net/spotify/" + artist_element['href']

            # Extract the total monthly listeners
            artist = artist_element.find_parent('div').find_parent('td').find_parent('tr')
            monthly_listeners = artist.find_all('td')[1].get_text()
            monthly_listeners = int(monthly_listeners.replace(',', ''))

            return link, monthly_listeners
        else:
            # Try to fetch another way
            spotify = SpotifyClient()
            artist_id = spotify.get_artist_id(artist_name)

            if artist_id:
                return f"https://kworb.net/spotify/artist/{artist_id}_songs.html", None

        return None, None

    def fetch_artist_information(self, artist_name):
        # Dictionary to store the artist information
        artist_information = {"Total Spotify Streams": None, "Total Spotify Monthly Listeners": None, "Total YouTube Views": None, "Most Streamed Songs": None}

        # Find artist link
        link, monthly_listeners = self.find_artist(artist_name)
        if not(link):
            return None

        # Store the total monthly listeners in the dictionary
        artist_information["Total Spotify Monthly Listeners"] = monthly_listeners

        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first <tbody> element
        tables = soup.find_all('tbody')

        if (not(tables)):
            return None

        # Get the total number of streams
        artist_information["Total Spotify Streams"] = get_total_number_of_streams(tables[0])
        artist_information["Total YouTube Views"] = get_total_youtube_views(artist_name)
        artist_information["Most Streamed Songs"] = get_most_streamed_songs(tables[1])

        return artist_information



def get_total_youtube_views(artist_name):
    url = f"https://kworb.net/youtube/artist/{artist_name.replace(' ', '').lower()}.html"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    youtube_stats_element = soup.find('td', text="Total views:")
    if (youtube_stats_element):
        youtube_views_text = youtube_stats_element.find_next('td').get_text()
        return int(youtube_views_text.replace(',', ''))

    return None

def get_most_streamed_songs(table):
    # Initialize a list to store dictionaries for each song
    songs = []

    # Find all songs in the table
    for tr in table.find_all('tr'):
        # Extract song title, number of streams, and Spotify track id
        song_title = tr.find('a').text
        number_of_streams = tr.find_all('td')[1].text.replace(',', '')
        spotify_track_id = tr.find('a')['href'].split('/')[-1]

        # Create a dictionary for the song and add it to the list
        song_dict = {
            "Song Title": song_title,
            "Number of Streams": int(number_of_streams),
            "Spotify Track Id": spotify_track_id
        }
        songs.append(song_dict)

    return songs

def get_total_number_of_streams(table):
        # Find the element that contains the total number of streams
        streams_element = table.find_all('td')[1]

        # Get the total number of streams
        total_streams = int(streams_element.get_text().replace(',', ''))
        return total_streams



if __name__ == "__main__":
    scraper = KworbScrapper()
    for artist_name in ["A Boogie Wit da Hoodie"]:
        artist_info = scraper.fetch_artist_information(artist_name)
        songs = artist_info["Most Streamed Songs"]

        most_streamed_song = scraper.find_most_streamed_song(songs, 2017, 2020)
        print(most_streamed_song)

