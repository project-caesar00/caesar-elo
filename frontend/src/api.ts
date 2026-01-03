import type {
    Website,
    WebsiteGrade,
    GradeSubmission,
    StackStats,
    Stats,
    ScrapeConfig,
    ScrapeJob,
    ComparisonPair,
    LeaderboardItem,
    AggregationResponse
} from './types';

// Use Vite env variable for production, fallback to localhost for dev
const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api';

async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
        const error = await res.text();
        throw new Error(error || `HTTP ${res.status}`);
    }
    return res.json();
}

export const api = {
    // --- Stack Review ---

    async getNextUngraded(): Promise<Website | null> {
        const res = await fetch(`${API_BASE}/stack/next`);
        if (!res.ok) throw new Error('Failed to get next website');
        const data = await res.json();
        return data || null;
    },

    async getStackStats(): Promise<StackStats> {
        const res = await fetch(`${API_BASE}/stack/stats`);
        return handleResponse<StackStats>(res);
    },

    async gradeWebsite(websiteId: number, grade: GradeSubmission): Promise<WebsiteGrade> {
        const res = await fetch(`${API_BASE}/websites/${websiteId}/grade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(grade),
        });
        return handleResponse<WebsiteGrade>(res);
    },

    async skipWebsite(websiteId: number): Promise<void> {
        const res = await fetch(`${API_BASE}/websites/${websiteId}/skip`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error('Failed to skip website');
    },

    // --- Websites ---

    async getWebsites(filters?: { is_graded?: boolean; is_designvorlage?: boolean; is_good_lead?: boolean }): Promise<Website[]> {
        const params = new URLSearchParams();
        if (filters?.is_graded !== undefined) params.append('is_graded', String(filters.is_graded));
        if (filters?.is_designvorlage !== undefined) params.append('is_designvorlage', String(filters.is_designvorlage));
        if (filters?.is_good_lead !== undefined) params.append('is_good_lead', String(filters.is_good_lead));

        const res = await fetch(`${API_BASE}/websites?${params}`);
        return handleResponse<Website[]>(res);
    },

    async getWebsite(id: number): Promise<Website> {
        const res = await fetch(`${API_BASE}/websites/${id}`);
        return handleResponse<Website>(res);
    },

    async addWebsite(url: string, name?: string): Promise<Website> {
        const res = await fetch(`${API_BASE}/websites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, name }),
        });
        return handleResponse<Website>(res);
    },

    // --- Scraping ---

    async startScrape(config: ScrapeConfig): Promise<ScrapeJob> {
        const res = await fetch(`${API_BASE}/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        return handleResponse<ScrapeJob>(res);
    },

    async getScrapeJobs(): Promise<ScrapeJob[]> {
        const res = await fetch(`${API_BASE}/scrape/jobs`);
        return handleResponse<ScrapeJob[]>(res);
    },

    async getScrapeJob(id: number): Promise<ScrapeJob> {
        const res = await fetch(`${API_BASE}/scrape/jobs/${id}`);
        return handleResponse<ScrapeJob>(res);
    },

    // --- Comparison (for later ELO features) ---

    async getComparisonPair(): Promise<ComparisonPair> {
        const res = await fetch(`${API_BASE}/compare`);
        return handleResponse<ComparisonPair>(res);
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

    // --- Leaderboard & Stats ---

    async getLeaderboard(limit = 50): Promise<LeaderboardItem[]> {
        const res = await fetch(`${API_BASE}/leaderboard?limit=${limit}`);
        return handleResponse<LeaderboardItem[]>(res);
    },

    async getStats(): Promise<Stats> {
        const res = await fetch(`${API_BASE}/stats`);
        return handleResponse<Stats>(res);
    },

    // --- Aggregation ---

    async aggregatePlaces(query: string, minRating?: number): Promise<AggregationResponse> {
        const res = await fetch(`${API_BASE}/aggregate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                min_rating: minRating,
            }),
        });
        return handleResponse<AggregationResponse>(res);
    },
};
