import React, {useState, useEffect} from 'react';

interface Session {
    start_time:sting;
    end_time: string;
    session_duration: number;
    total_playtime_minutes: number;
    unique_artists:string[];
    track_count: number;
    tracks: string[]
}

export function SessionSummary(){
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string| null>(null);

    useEffect(()=>{
        const fetchSessions = async () => {
            try {
                
            } catch (error) {
                
            }finally{}
        }
    });
}

export default SessionSummary