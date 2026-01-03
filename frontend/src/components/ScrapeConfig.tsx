import { useState } from 'react';
import { api } from '../api';
import type { ScrapeJob } from '../types';
import './ScrapeConfig.css';

const BUSINESS_TYPES = [
    'restaurant', 'cafe', 'bar', 'gym', 'spa', 'beauty_salon', 'hair_salon',
    'dentist', 'doctor', 'lawyer', 'accounting', 'real_estate_agency',
    'hotel', 'car_dealer', 'car_repair', 'clothing_store', 'jewelry_store',
    'furniture_store', 'florist', 'bakery'
];

export function ScrapeConfig() {
    const [location, setLocation] = useState('');
    const [radiusKm, setRadiusKm] = useState(10);
    const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [recentJobs, setRecentJobs] = useState<ScrapeJob[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const toggleType = (type: string) => {
        setSelectedTypes(prev =>
            prev.includes(type)
                ? prev.filter(t => t !== type)
                : [...prev, type]
        );
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!location.trim()) {
            setError('Please enter a location');
            return;
        }

        setIsLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const job = await api.startScrape({
                location: location.trim(),
                radius_km: radiusKm,
                business_types: selectedTypes,
            });
            setSuccess(`Scrape job started! Job ID: ${job.id}`);
            setRecentJobs(prev => [job, ...prev]);
            setLocation('');
            setSelectedTypes([]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start scrape');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="scrape-config">
            <h2>Scrape Websites from Google Maps</h2>

            <form onSubmit={handleSubmit} className="scrape-form">
                <div className="form-group">
                    <label htmlFor="location">Location</label>
                    <input
                        id="location"
                        type="text"
                        placeholder="e.g., Berlin, Germany"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="radius">Radius: {radiusKm} km</label>
                    <input
                        id="radius"
                        type="range"
                        min="1"
                        max="50"
                        value={radiusKm}
                        onChange={(e) => setRadiusKm(Number(e.target.value))}
                    />
                </div>

                <div className="form-group">
                    <label>Business Types (optional)</label>
                    <div className="type-chips">
                        {BUSINESS_TYPES.map(type => (
                            <button
                                key={type}
                                type="button"
                                className={`type-chip ${selectedTypes.includes(type) ? 'selected' : ''}`}
                                onClick={() => toggleType(type)}
                            >
                                {type.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                </div>

                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}

                <button type="submit" className="submit-btn" disabled={isLoading}>
                    {isLoading ? 'Starting...' : '🔍 Start Scraping'}
                </button>
            </form>

            {recentJobs.length > 0 && (
                <div className="recent-jobs">
                    <h3>Recent Jobs</h3>
                    {recentJobs.map(job => (
                        <div key={job.id} className="job-card">
                            <span className="job-location">{job.location}</span>
                            <span className={`job-status ${job.status}`}>{job.status}</span>
                            <span className="job-found">{job.websites_found} found</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
