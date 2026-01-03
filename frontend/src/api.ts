const API_BASE = 'http://localhost:8000/api';

export interface Website {
    id: number;
    url: string;
    name: string | null;
    description: string | null;
    screenshot_path: string | null;
    elo_rating: number;
    matches_played: number;
    wins: number;
    losses: number;
    created_at: string;
}

export interface ComparisonPair {
    website_a: Website;
    website_b: Website;
}

export interface LeaderboardItem extends Website {
    rank: number;
}

export interface Stats {
    total_websites: number;
    total_comparisons: number;
    avg_elo: number;
}

export const api = {
    async getComparisonPair(): Promise<ComparisonPair> {
        const res = await fetch(`${API_BASE}/compare`);
        if (!res.ok) throw new Error('Failed to get comparison pair');
        return res.json();
    },

    async submitComparison(websiteAId: number, websiteBId: number, winnerId: number | null): Promise<void> {
        const res = await fetch(`${API_BASE}/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                website_a_id: websiteAId,
                website_b_id: websiteBId,
                winner_id: winnerId,
            }),
        });
        if (!res.ok) throw new Error('Failed to submit comparison');
    },

    async getLeaderboard(limit = 50): Promise<LeaderboardItem[]> {
        const res = await fetch(`${API_BASE}/leaderboard?limit=${limit}`);
        if (!res.ok) throw new Error('Failed to get leaderboard');
        return res.json();
    },

    async getStats(): Promise<Stats> {
        const res = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error('Failed to get stats');
        return res.json();
    },

    async addWebsite(url: string, name?: string): Promise<Website> {
        const res = await fetch(`${API_BASE}/websites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, name }),
        });
        if (!res.ok) throw new Error('Failed to add website');
        return res.json();
    },
};
