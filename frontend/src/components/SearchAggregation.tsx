import { useState } from 'react';
import { api } from '../api';
import type { PlaceResult } from '../types';
import './SearchAggregation.css';

export function SearchAggregation() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<PlaceResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchedQuery, setSearchedQuery] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!query.trim()) return;

        setIsLoading(true);
        setError(null);
        setResults([]);

        try {
            const response = await api.aggregatePlaces(query.trim());
            setResults(response.results);
            setSearchedQuery(response.query);
        } catch (err) {
            if (err instanceof Error) {
                // Check for quota error
                if (err.message.includes('429') || err.message.toLowerCase().includes('quota')) {
                    setError('API Limit erreicht, bitte später versuchen.');
                } else {
                    setError(err.message);
                }
            } else {
                setError('Ein unbekannter Fehler ist aufgetreten.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const getRatingCountClass = (count: number): string => {
        if (count >= 1000) return 'high';
        if (count >= 500) return 'medium';
        return '';
    };

    return (
        <div className="search-aggregation">
            <h2>Daten Aggregieren</h2>

            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Suchbegriff eingeben, z.B. Sushi Berlin"
                    className="search-input"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className="search-btn"
                    disabled={isLoading || !query.trim()}
                >
                    {isLoading ? (
                        <>
                            <span className="spinner"></span>
                            Suche...
                        </>
                    ) : (
                        'Daten aggregieren'
                    )}
                </button>
            </form>

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {!isLoading && !error && searchedQuery && results.length === 0 && (
                <div className="no-results">
                    Keine Locations für "{searchedQuery}" gefunden.
                </div>
            )}

            {results.length > 0 && (
                <>
                    <div className="results-summary">
                        <strong>{results.length}</strong> Ergebnisse für "{searchedQuery}"
                        – sortiert nach Anzahl Bewertungen
                    </div>

                    <div className="results-table-container">
                        <table className="results-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Name</th>
                                    <th>Bewertungen</th>
                                    <th>Score</th>
                                    <th>Website</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((place) => (
                                    <tr key={place.google_place_id}>
                                        <td className={`rank-cell ${place.rank <= 3 ? 'top-3' : ''}`}>
                                            {place.rank}
                                        </td>
                                        <td>{place.name}</td>
                                        <td>
                                            <span className={`rating-count ${getRatingCountClass(place.rating_count)}`}>
                                                {place.rating_count >= 1000 && <span className="fire">🔥</span>}
                                                {place.rating_count.toLocaleString('de-DE')}
                                            </span>
                                        </td>
                                        <td>
                                            {place.rating_score ? (
                                                <span className="rating-score">
                                                    <span className="star">★</span>
                                                    {place.rating_score.toFixed(1)}
                                                </span>
                                            ) : (
                                                <span className="no-website">—</span>
                                            )}
                                        </td>
                                        <td>
                                            {place.website_url ? (
                                                <a
                                                    href={place.website_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="website-link"
                                                >
                                                    🔗 Website
                                                </a>
                                            ) : (
                                                <span className="no-website">Keine Website</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
}
