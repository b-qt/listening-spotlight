import React, { useState, useEffect } from 'react';

interface Session {
    start_time: sting;
    end_time: string;
    session_duration: number;
    total_playtime_minutes: number;
    unique_artists: string[];
    track_count: number;
    tracks: string[]
}

export function SessionSummary() {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await fetch('../../python/data/listening_sessions.json');

                if (!response.ok) {
                    throw new Error(`Error fetching .. ${response.status}`);
                }
                const data: SessionData[] = await response.json();
                setSessions(data);
            } catch (error: any) {
                setError(`Failed to load Spotify session data: ${err.message}. Make sure the Python script generated spotify_sessions.json.`);
                console.error("Error fetching sessions.json:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchSessions();
    }, []);

    if (loading) {
        return <div>Loading Spotify sessions...</div>;
    }

    if (error) {
        return <div style={{ color: 'red' }}>Error: {error}</div>;
    }

    if (sessions.length === 0) {
        return <div>No Spotify sessions found. Run the Python script or listen to music!</div>;
    }

    return (
        <div style={{ padding: '15px', background: 'rgba(0,0,0,0.7)', borderRadius: '8px', color: 'white', fontSize: '0.9em', maxWidth: '300px' }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '1em' }}>Your Spotify Sessions:</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: '200px', overflowY: 'auto' }}>
                {sessions.map((session, index) => (
                    <li key={index} style={{ marginBottom: '10px', borderBottom: '1px solid #444', paddingBottom: '5px' }}>
                        <strong>Session {index + 1}:</strong><br />
                        Start: {new Date(session.session_start_utc).toLocaleString()}<br />
                        Duration: {Math.round(session.session_duration_seconds / 60)} min<br />
                        Tracks: {session.track_count}<br />
                        Artists: {session.unique_artists.join(', ')}<br />
                        {/* Tracks List: {session.tracks.join(', ')} */}
                    </li>
                ))}
            </ul>
        </div>
    );

}

export default SessionSummary