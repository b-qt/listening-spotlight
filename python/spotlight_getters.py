"""
Fetches and processes user data from the Spotify API and saves it to JSON files.

This script retrieves a user's followed artists, top artists, top tracks, and
listening sessions, then outputs them to a specified data directory.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

import spotipy # type: ignore
from spotipy.oauth2 import SpotifyOAuth # type: ignore

# --- Constants ---
# It's good practice to define constants at the top for easy modification.
SCOPES = "user-read-recently-played user-library-read user-follow-read user-top-read"
OUTPUT_DIR = os.path.join('..', 'public', 'data')

class SpotifyDataFetcher:
    """A class to fetch and process data from the Spotify API."""

    def __init__(self, spotify_client: spotipy.Spotify):
        """
        Initializes the fetcher with an authenticated Spotipy client.

        Args:
            spotify_client (spotipy.Spotify): An authenticated Spotipy instance.
        """
        if not spotify_client:
            raise ValueError("An authenticated Spotipy client is required.")
        self.sp = spotify_client

    def get_followed_artists(self) -> List[str]:
        """Fetches the names of all artists the user follows."""
        print("Fetching followed artists...")
        response = self.sp.current_user_followed_artists(limit=50)
        artists = response['artists']['items']
        
        # Paginate to get all followed artists
        while response['artists']['next']:
            response = self.sp.next(response['artists'])
            artists.extend(response['artists']['items'])

        return [artist['name'] for artist in artists]

    def get_top_artists(self, limit: int = 20, time_range: str = 'long_term') -> List[str]:
        """Fetches the user's top artists."""
        print(f"Fetching top {limit} artists ({time_range})...")
        response = self.sp.current_user_top_artists(time_range=time_range, limit=limit)
        return [item['name'] for item in response['items']]

    def get_top_tracks(self, limit: int = 20, time_range: str = 'long_term') -> List[str]:
        """Fetches the user's top tracks."""
        print(f"Fetching top {limit} tracks ({time_range})...")
        response = self.sp.current_user_top_tracks(time_range=time_range, limit=limit)
        return [item['name'] for item in response['items']]

    def get_listening_sessions(self, min_sessions: int = 5, session_break_hours: float = 1.0) -> List[Dict[str, Any]]:
        """
        Fetches and processes user's listening history into distinct sessions.
        """
        print(f"Fetching listening history to find at least {min_sessions} sessions...")
        all_tracks = self._fetch_all_recent_tracks()
        
        if not all_tracks:
            return []

        # The API returns newest first; reverse for chronological processing.
        all_tracks.reverse()
        
        sessions = self._process_tracks_into_sessions(all_tracks, session_break_hours)
        
        print(f"Found {len(sessions)} sessions. Formatting output...")
        return self._format_sessions_output(sessions)

    def _fetch_all_recent_tracks(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Helper to paginate through recently played tracks."""
        all_tracks = []
        results = self.sp.current_user_recently_played(limit=50)
        
        while results and results['items'] and len(all_tracks) < limit:
            all_tracks.extend(results['items'])
            if 'next' in results and results['next']:
                results = self.sp.next(results)
            else:
                break # No more pages
        
        return all_tracks

    @staticmethod
    def _process_tracks_into_sessions(tracks: List[Dict[str, Any]], break_hours: float) -> List[List[Dict[str, Any]]]:
        """Processes a flat list of tracks into a nested list of sessions."""
        if not tracks:
            return []

        session_break_seconds = break_hours * 3600
        sessions = []
        current_session = [tracks[0]]

        for i in range(1, len(tracks)):
            prev_track_time = datetime.fromisoformat(tracks[i-1]['played_at'].replace('Z', '+00:00'))
            curr_track_time = datetime.fromisoformat(tracks[i]['played_at'].replace('Z', '+00:00'))
            
            time_gap = (curr_track_time - prev_track_time).total_seconds()

            if time_gap > session_break_seconds:
                sessions.append(current_session)
                current_session = [tracks[i]]
            else:
                current_session.append(tracks[i])
        
        sessions.append(current_session) # Add the last session
        return sessions

    @staticmethod
    def _format_sessions_output(sessions: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Formats the raw session data into a clean, final structure."""
        formatted_sessions = []
        for session_tracks in sessions:
            formatted_sessions.append({
                "start_time": session_tracks[0]['played_at'],
                "end_time": session_tracks[-1]['played_at'],
                "track_count": len(session_tracks),
                "tracks": [
                    f"{t['track']['artists'][0]['name']} - {t['track']['name']}"
                    for t in session_tracks
                ],
                "images": [
                    t['track']['album']['images'][2]['url']
                    for t in session_tracks if t['track']['album']['images']
                ]
            })
        return formatted_sessions


def save_to_json(data: list, filename: str):
    """Saves a list of dictionaries to a JSON file, creating directories if needed."""
    try:
        # Ensure the directory exists before trying to write the file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully saved data to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON file {filename}: {e}")


def main():
    """Main function to authenticate, fetch data, and save it."""
    print("--- Starting Spotify Data Fetcher ---")

    # --- Authentication ---
    # This is the standard way to handle authentication securely.
    try:
        auth_manager = SpotifyOAuth(
            scope=SCOPES,
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        )
        sp_client = spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("Please ensure your SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI environment variables are set.")
        return # Exit the script if auth fails

    # --- Fetching Data ---
    fetcher = SpotifyDataFetcher(sp_client)

    followed_artists = fetcher.get_followed_artists()
    top_artists = fetcher.get_top_artists()
    top_tracks = fetcher.get_top_tracks()
    listening_sessions = fetcher.get_listening_sessions()

    # --- Saving Data ---
    print("\n--- Saving all data to JSON files ---")
    save_to_json(followed_artists, os.path.join(OUTPUT_DIR, 'followed_artists.json'))
    save_to_json(top_artists, os.path.join(OUTPUT_DIR, 'top_artists.json'))
    save_to_json(top_tracks, os.path.join(OUTPUT_DIR, 'top_tracks.json'))
    save_to_json(listening_sessions, os.path.join(OUTPUT_DIR, 'listening_sessions.json'))
    
    print("\n--- Script finished successfully! ---")


if __name__ == "__main__":
    main()