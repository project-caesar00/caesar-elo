import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Website } from '../types';
import './WebsiteList.css';

interface WebsiteListProps {
    filter: 'designvorlage' | 'good_lead' | 'graded';
    title: string;
}

export function WebsiteList({ filter, title }: WebsiteListProps) {
    const [websites, setWebsites] = useState<Website[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            setIsLoading(true);
            try {
                const filters = filter === 'designvorlage'
                    ? { is_designvorlage: true }
                    : filter === 'good_lead'
                        ? { is_good_lead: true }
                        : { is_graded: true };

                const data = await api.getWebsites(filters);
                setWebsites(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load');
            } finally {
                setIsLoading(false);
            }
        };
        load();
    }, [filter]);

    if (isLoading) {
        return <div className="website-list loading">Loading...</div>;
    }

    if (error) {
        return <div className="website-list error">Error: {error}</div>;
    }

    if (websites.length === 0) {
        return (
            <div className="website-list empty">
                <div className="empty-state">
                    <h2>No {title} yet</h2>
                    <p>Start reviewing websites to populate this list.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="website-list">
            <h2>{title} ({websites.length})</h2>
            <div className="website-grid">
                {websites.map((website) => (
                    <div key={website.id} className="website-card">
                        <div className="website-card-header">
                            <h3>{website.name || 'Unnamed'}</h3>
                            <div className="flags">
                                {website.is_designvorlage && <span className="flag designvorlage">🎨</span>}
                                {website.is_good_lead && <span className="flag good-lead">🎯</span>}
                            </div>
                        </div>
                        <a href={website.url} target="_blank" rel="noopener noreferrer" className="website-url">
                            {website.url}
                        </a>
                        {website.business_type && (
                            <span className="business-type">{website.business_type}</span>
                        )}
                        <div className="website-meta">
                            <span>ELO: {Math.round(website.elo_rating)}</span>
                            {website.graded_at && (
                                <span>Graded: {new Date(website.graded_at).toLocaleDateString()}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
