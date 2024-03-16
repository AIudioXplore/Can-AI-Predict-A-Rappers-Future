import datetime
import time

from enum import Enum

import pandas as pd

from Scrappers.billboard_scrapper import BillboardScrapper
from Scrappers.songstats_scrapper import SongStatsScrapper
from Scrappers.spotify_scrapper import SpotifyClient
from Scrappers.riaa_scrapper import RiaaScrapper
from Scrappers.kworb_scrapper import KworbScrapper
from Scrappers.kworb_scrapper import get_total_youtube_views

class DatasetColumns(Enum):
    # DATA COLUMNS
    ARTIST_NAME = 'Artist Name'
    PRIMARY_GENRE = 'Primary Genre'
    BIRTHDAY = 'Birthday'
    DEBUT_ALBUM_YEAR = 'Year Debut Studio Album Released'
    DEBUT_ALBUM_NAME = 'Debut Album'
    EARLIEST_MONTHLY_LISTENERS = 'Earliest Monthly Listeners'
    MONTHLY_LISTENERS_3_YEARS_LATER = 'Monthly Listeners 3 Years Later or Latest'
    MOST_STREAMED_SONG_WITHIN_3_YEARS = 'Most Streamed Song Within 3 Years of Debut Album'
    MOST_STREAMED_SONG_WITHIN_3_YEARS_NUMBER_STREAMS = 'Most Streamed Song Within 3 Years of Debut Album Number of Streams'

    # AI OPINION COLUMNS
    CHAT_GPT_LYRIC_RATING = 'ChatGPT Lyric Rating'
    CHAT_GPT_LANGUAGE_WORDPLAY_RATING = 'ChatGPT Language and Wordplay Rating'
    CHAT_GPT_ORIGIANALITY_UNIQUNESS_RATING = 'ChatGPT Originality and Uniqueness Rating'
    CHAT_GPT_MEMORABILITY_RATING = 'ChatGPT Memorability Rating'

    GROK_LYRIC_RATING = 'Grok Lyric Rating'
    GROK_LANGUAGE_WORDPLAY_RATING = 'Grok Language and Wordplay Rating'
    GROK_ORIGIANALITY_UNIQUNESS_RATING = 'Grok Originality and Uniqueness Rating'
    GROK_MEMORABILITY_RATING = 'Grok Memorability Rating'

    # PREDICTOR COLUMNS
    GENDER = 'Gender'
    CHAT_GPT_SCORE = 'ChatGPT Score'
    CHAT_GPT_HIGH_ACHIEVEMENT_SCORE_PREDICTION = 'ChatGPT High Achievement Score Prediction'# Might not be needed
    GROK_SCORE = 'Grok Score'
    GROK_HIGH_ACHIEVEMENT_SCORE_PREDICTION = 'Grok High Achievement Score Prediction' # Might not be needed
    DEBUT_ALUM_FIRST_WEEK_SALES = 'Debut Album First Week Sales'
    AGE_AT_DEBUT_ALBUM = 'Age At The Time of First Released Album'
    PERCENT_INCREASE_MONTHLY_LISTENERS = 'Percent Increase In Monthly Listeners'
    BILLBOARD_100_ENTRIES_WITHIN_3_YEARS = 'Billboard 100 Entries Within 3 Years of Debut Album'
    AVERAGE_DAYS_BETWEEN_RELEASE_DATES = 'Average Number of Days Between Release Dates'
    RIAA_CERTIFICATIONS_WITHIN_3_YEARS = 'RIAA Certifications Within 3 Years of Debut Album'

    # ACHIEVMENT SCORE CONTRIBUTION COLUMNS
    TOTAL_RIAA_CERTIFICATIONS = 'Total RIAA Certifications'
    TOTAL_BILLBOARD_100_ENTRIES = 'Total Billboard 100 Entries'
    TOTAL_SPOTIFY_MONTHLY_LISTENERS = 'Total Spotify Monthly Listeners'
    TOTAL_SPOTIFY_PLAYLIST_APPEARANCES = 'Total Spotify Playlists Appearances'
    TOTAL_YOUTUBE_VIEWS = 'Total YouTube Views'
    TOTAL_SPOTIFY_STREAMS = 'Total Spotify Streams'

    # TARGET COLUMN
    ACHIEVEMENT_SCORE = 'Achievement Score'

if  __name__ == "__main__":
    # Open dataset
    df = pd.read_excel('Artists_Dataset.xlsx')

    # Initialize scrappers
    spotify = SpotifyClient()
    billboard = BillboardScrapper()
    kworb = KworbScrapper()

    # Get list of all artists in dataset
    artists = df[DatasetColumns.ARTIST_NAME.value].tolist()

    for index, artist in enumerate(artists):
        try:
            # Check if the artist 'Age At The Time of First Released Album' is already in the dataset
            if pd.isna(df[DatasetColumns.AGE_AT_DEBUT_ALBUM.value][index]):
                if isinstance(df[DatasetColumns.BIRTHDAY.value][index], datetime.datetime):
                    # The object is already a datetime object
                    birthday = df[DatasetColumns.BIRTHDAY.value][index]
                else:
                    # Convert the string to a datetime object
                    birthday = datetime.datetime.strptime(df[DatasetColumns.BIRTHDAY.value][index], '%Y-%m-%d %H:%M:%S')

                print(f"Fetching age of {artist} at the time of debut album release...")
                age = spotify.get_age_of_artist_when_album_was_released(artist, birthday, df[DatasetColumns.DEBUT_ALBUM_NAME.value][index])

                if (age):
                    # Update age for Age At The Time of First Released Album column
                    print(f"Successfully fetched age of {artist} at the time of debut album release.")
                    df.at[index, 'Age At The Time of First Released Album'] = age

            # Check if the artist 'Earliest Monthly Listeners' is already in the dataset
            if pd.isna(df[DatasetColumns.EARLIEST_MONTHLY_LISTENERS.value][index]):
                songstats = SongStatsScrapper()
                artist_id = songstats.fetch_artist_id(artist)

                if (artist_id):
                    print(f"Fetching monthly listeners for {artist} with id {artist_id}...")
                    monthly_listeners = songstats.fetch_monthly_listeners(artist_id)

                    # Fetch the earliest and latest monthly listeners from the starting date of data
                    # to three years later or the last entry in the data
                    earliest, latest = songstats.fetch_earliest_to_latest_monthly_listeners(monthly_listeners)

                    # Update the dataset with the earliest and latest monthly listeners
                    print(f"Successfully fetched earliest and latest monthly listeners for {artist}.")

                    df.at[index, DatasetColumns.EARLIEST_MONTHLY_LISTENERS.value] = earliest[1]
                    df.at[index, DatasetColumns.MONTHLY_LISTENERS_3_YEARS_LATER.value] = latest[1]

                songstats.close()

                # Wait for three seconds to avoid throttling
                time.sleep(3)

            # Check if the artist 'Billboard 100 Entries Within 3 Years' is already in the dataset
            if pd.isna(df[DatasetColumns.BILLBOARD_100_ENTRIES_WITHIN_3_YEARS.value][index]):
                print(f"Fetching Billboard 100 entries for {artist}...")
                entries = billboard.fetch_billboard_100_entries(artist)

                count = None

                if (entries):
                    # Define the range of years to check for
                    start_year = df[DatasetColumns.DEBUT_ALBUM_YEAR.value][index]
                    end_year = start_year + 3

                    # Count the number of entries within the specified range of years
                    count = sum(1 for entry in entries if start_year <= entry['debut_date'].year <= end_year)

                # Update the dataset with the number of entries
                df.at[index, DatasetColumns.BILLBOARD_100_ENTRIES_WITHIN_3_YEARS.value] = count

                # Wait for three seconds to avoid throttling
                time.sleep(3)

            # Check if the artist 'Average Number of Days Between Release Dates' is already in the dataset
            if pd.isna(df[DatasetColumns.AVERAGE_DAYS_BETWEEN_RELEASE_DATES.value][index]):
                print(f"Fetching average number of days between release dates for {artist}...")
                average_days = spotify.get_average_days_between_releases(artist, df[DatasetColumns.DEBUT_ALBUM_NAME.value][index])

                # Update the dataset with the average number of days between release dates
                df.at[index, DatasetColumns.AVERAGE_DAYS_BETWEEN_RELEASE_DATES.value] = average_days

            # Check if the artist 'RIAA Cerifications Within 3 Years of Debut Album' is already in the dataset
            if pd.isna(df[DatasetColumns.RIAA_CERTIFICATIONS_WITHIN_3_YEARS.value][index]):
                print(f"Fetching RIAA certifications for {artist}...")
                riaa = RiaaScrapper()
                certifications = riaa.fetch_riaa_certifications(artist, df[DatasetColumns.DEBUT_ALBUM_YEAR.value][index])

                count = None

                if (certifications):
                    print(f"Successfully fetched RIAA certifications within 3 years of debut album for {artist}.")
                    count = len(certifications)

                # Update the dataset with the number of entries
                df.at[index, DatasetColumns.RIAA_CERTIFICATIONS_WITHIN_3_YEARS.value] = count

                # Wait for three seconds to avoid throttling
                time.sleep(3)

                riaa.close()

            # Check if the artist 'Total RIAA Certificationsm' is already in the dataset
            if pd.isna(df[DatasetColumns.TOTAL_RIAA_CERTIFICATIONS.value][index]):
                print(f"Fetching total RIAA certifications for {artist}...")
                riaa = RiaaScrapper()
                certifications = riaa.fetch_riaa_certifications(artist)

                count = None

                if (certifications):
                    print(f"Successfully fetched RIAA certifications for {artist}.")
                    count = len(certifications)

                # Update the dataset with the number of entries
                df.at[index, DatasetColumns.TOTAL_RIAA_CERTIFICATIONS.value] = count

                # Wait for three seconds to avoid throttling
                time.sleep(3)

                riaa.close()

            # Check if the artist 'Total Billboard 100 Entries' is already in the dataset
            if pd.isna(df[DatasetColumns.TOTAL_BILLBOARD_100_ENTRIES.value][index]):
                print(f"Fetching total Billboard 100 entries for {artist}...")
                entries = billboard.fetch_billboard_100_entries(artist)

                count = None

                if (entries):
                    count = len(entries)

                # Update the dataset with the number of entries
                df.at[index, DatasetColumns.TOTAL_BILLBOARD_100_ENTRIES.value] = count

                # Wait for three seconds to avoid throttling
                time.sleep(3)

            # Check if the artist 'Total Spotify Monthly Listeners' or 'Total Spotify Streams' is already in the dataset
            if pd.isna(df[DatasetColumns.TOTAL_SPOTIFY_MONTHLY_LISTENERS.value][index] or pd.isna(df[DatasetColumns.TOTAL_SPOTIFY_STREAMS.value][index])):
                print(f"Fetching Total Spotify monthly listeners and streams for {artist}...")
                artist_information = kworb.fetch_artist_information(artist)

                if (artist_information):
                    print(f"Successfully fetched Total Spotify monthly listeners and streams for {artist}.")

                    # Update the dataset with the number of monthly listeners
                    if (pd.isna(df[DatasetColumns.TOTAL_SPOTIFY_MONTHLY_LISTENERS.value][index])):
                        df.at[index, DatasetColumns.TOTAL_SPOTIFY_MONTHLY_LISTENERS.value] = artist_information['Total Spotify Monthly Listeners']

                    # Update the dataset with the total number of streams
                    if (pd.isna(df[DatasetColumns.TOTAL_SPOTIFY_STREAMS.value][index])):
                        df.at[index, DatasetColumns.TOTAL_SPOTIFY_STREAMS.value] = artist_information['Total Spotify Streams']

            # Check if the artist 'Total YouTube Views' is already in the dataset
            if pd.isna(df[DatasetColumns.TOTAL_YOUTUBE_VIEWS.value][index]):
                print(f"Fetching Total YouTube views for {artist}...")
                youtube_views = get_total_youtube_views(artist)

                if (youtube_views):
                    print(f"Successfully fetched Total YouTube views for {artist}.")
                    df.at[index, DatasetColumns.TOTAL_YOUTUBE_VIEWS.value] = youtube_views
                else:
                    print(f"Could not fetch Total YouTube views for {artist}.")

            # Check if the artist 'Most Streamed Song Within 3 Years' is already in the dataset
            if pd.isna(df[DatasetColumns.MOST_STREAMED_SONG_WITHIN_3_YEARS.value][index]):
                print(f"Fetching most streamed song within 3 years of debut album for {artist}...")
                artist_information = kworb.fetch_artist_information(artist)

                if (artist_information and artist_information['Most Streamed Songs']):
                    most_streamed_songs = artist_information['Most Streamed Songs']

                    # Get the most streamed song within 3 years of debut album
                    most_streamed_song = spotify.find_most_streamed_song(most_streamed_songs,
                                                                 df[DatasetColumns.DEBUT_ALBUM_YEAR.value][index],
                                                                 df[DatasetColumns.DEBUT_ALBUM_YEAR.value][index] + 3)

                    # Extract the song title and number of streams
                    song_title = most_streamed_song["Song Title"]
                    number_of_streams = most_streamed_song["Number of Streams"]

                    print(f"Most Streamed Song: {song_title} with {number_of_streams} streams.")

                    # Update the dataset with the most streamed song within 3 years of debut album
                    df.at[index, DatasetColumns.MOST_STREAMED_SONG_WITHIN_3_YEARS.value] = song_title
                    df.at[index, DatasetColumns.MOST_STREAMED_SONG_WITHIN_3_YEARS_NUMBER_STREAMS.value] = number_of_streams
                else:
                    print(f"Could not fetch most streamed song within 3 years of debut album for {artist}.")

            # Check if the artist 'Total Spotify Playlist Appearances' is already in the dataset
            if pd.isna(df[DatasetColumns.TOTAL_SPOTIFY_PLAYLIST_APPEARANCES.value][index]):
                print(f"Fetching Total Spotify playlist appearances for {artist}...")
                songstats = SongStatsScrapper()
                artist_id = songstats.fetch_artist_id(artist)
                playlist_appearances = songstats.fetch_total_playlists(artist_id)

                if (playlist_appearances):
                    print(f"Successfully fetched Total Spotify playlist appearances for {artist}.")
                    df.at[index, DatasetColumns.TOTAL_SPOTIFY_PLAYLIST_APPEARANCES.value] = playlist_appearances

                # Wait for three seconds to avoid throttling
                time.sleep(3)

                songstats.close()

            # Print empty line to separate artists
            print()

        except Exception as e:
            print(f"An error occurred while fetching data for {artist}: {e}")

            # Save the updated dataset with existing data in case of an error
            df.to_excel('Artists_Dataset_Updated.xlsx', index=False)

            print()

    # Save the updated dataset
    df.to_excel('Artists_Dataset_Updated.xlsx', index=False)

