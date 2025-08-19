import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import os, datetime, time
    from datetime import datetime, timedelta, timezone

    import spotipy as spot
    from spotipy.oauth2 import SpotifyOAuth
    return SpotifyOAuth, datetime, os, spot


@app.cell
def _(SpotifyOAuth, os, spot):
    scope = "user-read-recently-played user-library-read user-follow-read user-top-read"
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_url = os.getenv("SPOTIFY_REDIRECT_URI")

    sp = spot.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_url,
            scope=scope,
        )
    )
    return (sp,)


@app.cell
def _():
    import json 

    def save_to_json(data: list, filename: str):
        """Saves a list of dictionaries to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # json.dump writes the data to the file
                # indent=2 makes the file human-readable
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved data to {filename}")
        except Exception as e:
            print(f"Error saving to JSON file: {e}")

    return (save_to_json,)


@app.cell
def _(SpotifyOAuth, save_to_json, sp):
    def get_followed_artists(spotify_client:SpotifyOAuth=sp):
        response = spotify_client.current_user_followed_artists()
        artist_names = []
        for idx in response['artists']['items']:
            artist_names.append(idx['name'])

        return artist_names

    followed_artists = get_followed_artists()
    save_to_json(followed_artists, './data/followed_artists.json')
    return


@app.cell
def _(SpotifyOAuth, save_to_json, sp):
    def get_top_artists(spotify_client:SpotifyOAuth=sp, lim:int=3):
        response = spotify_client.current_user_top_artists(time_range='long_term', limit= lim)
        top_artist_names = []
        for idx in response['items']:
            top_artist_names.append(idx['name'])
        return top_artist_names

    top_artists = get_top_artists()
    save_to_json(top_artists, './data/top_artists.json')
    return


@app.cell
def _(SpotifyOAuth, save_to_json, sp):
    def get_top_tracks(spotify_client:SpotifyOAuth=sp, lim:int=10):
        response = spotify_client.current_user_top_tracks(time_range='long_term', limit= lim)
        top_artist_names = []
        for idx in response['items']:
            top_artist_names.append(idx['name'])
        return top_artist_names

    top_tracks = get_top_tracks()
    save_to_json(top_tracks, './data/top_tracks.json')
    return


@app.cell
def _(sp):
    sp.current_user_recently_played()
    return


@app.cell
def _(SpotifyOAuth, datetime, save_to_json, sp):
    def _process_tracks_into_sessions(track_list: list, 
                                      session_break_hours: float) -> list:
        """Helper function to process a list of tracks into sessions."""
        if not track_list:
            return []

        # The API returns newest to oldest; we reverse to process chronologically.
        track_list.reverse()

        sessions = []
        current_session = [track_list[0]]
        session_break_seconds = session_break_hours * 3600

        for i in range(1, len(track_list)):
            current_track = track_list[i]
            previous_track = track_list[i-1]

            current_time = datetime.fromisoformat(current_track['played_at'].replace('Z', '+00:00'))
            previous_time = datetime.fromisoformat(previous_track['played_at'].replace('Z', '+00:00'))

            time_gap_seconds = (current_time - previous_time).total_seconds()

            if time_gap_seconds > session_break_seconds:
                sessions.append(current_session)
                current_session = [current_track]
            else:
                current_session.append(current_track)

        sessions.append(current_session)

        return sessions

    def get_listening_sessions(spotify_client:SpotifyOAuth=sp, 
                               min_sessions: int = 3, 
                               session_break_hours: float = 1.0,
                               max_tracks_to_scan: int = 1000) -> list:
        """
        Fetches a user's recently played tracks until at least `min_sessions` are found.

        Args:
            sp (spotipy.Spotify): An authenticated Spotipy client instance.
            min_sessions (int): The target number of sessions to find.
            session_break_hours (float): The hours of inactivity that define a new session.
            max_tracks_to_scan (int): A safeguard to prevent fetching too much history.

        Returns:
            list: A list of formatted session dictionaries.
        """

        all_tracks = []
        before_cursor = None
        found_sessions = []

        print(f"Fetching history until at least {min_sessions} sessions are found...")

        # --- The "Fetch-Process-Check" Loop ---
        while True:
            try:
                results = spotify_client.current_user_recently_played(limit=50, before=before_cursor)
                if not results or not results['items']:
                    print("-> Reached the end of listening history.")
                    break # No more tracks to fetch

                all_tracks.extend(results['items'])
                print(f"  Fetched {len(all_tracks)} total tracks...")

                # Re-process the entire list of tracks to see how many sessions we have now
                found_sessions = _process_tracks_into_sessions(list(all_tracks), session_break_hours)
                print(f"  Currently found {len(found_sessions)} sessions.")

                # Check our exit conditions
                if len(found_sessions) >= min_sessions:
                    print(f"\t\t-> Success! Found {len(found_sessions)} sessions. Stopping.")
                    break

                if len(all_tracks) >= max_tracks_to_scan:
                    print(f"\t\t-> Reached scan limit of {max_tracks_to_scan} tracks. Stopping.")
                    break

                # If we need to continue, get the cursor for the next page
                before_cursor = results['cursors']['before']

            except Exception as e:
                print(f"An error occurred during fetching: {e}")
                break

        if not found_sessions:
            return []

        # --- Clean up the output for a professional result ---
        final_sessions_data = []
        for session_tracks in found_sessions:
            final_sessions_data.append({
                "start_time": session_tracks[0]['played_at'],
                "end_time": session_tracks[-1]['played_at'],
                "track_count": len(session_tracks),
                "tracks": [
                    f"{t['track']['artists'][0]['name']} - {t['track']['name']}" 
                    for t in session_tracks
                ],
                "images": [im['track']['album']['images'][2]['url'] for im in session_tracks]
            })

        return final_sessions_data


    listening_sessions = get_listening_sessions()

    listening_sessions,save_to_json(listening_sessions, './data/listening_sessions.json')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
