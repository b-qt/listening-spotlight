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

const sessionPath = `${process.env.PUBLIC_URL}/data/listening_sessions.json`;
export function SessionSummary() {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await fetch(sessionPath);

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

    return [sessions];

}

export default SessionSummary