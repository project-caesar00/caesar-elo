// Types for the Caesar ELO website classifier

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
    is_designvorlage: boolean;
    is_good_lead: boolean;
    is_graded: boolean;
    graded_at: string | null;
    business_type: string | null;
    address: string | null;
    phone: string | null;
    created_at: string;
}

export interface WebsiteGrade {
    id: number;
    website_id: number;
    overall_aesthetic: number | null;
    color_harmony: number | null;
    typography_quality: number | null;
    layout_spacing: number | null;
    imagery_quality: number | null;
    visual_hierarchy: number | null;
    mobile_responsiveness: number | null;
    notes: Record<string, string>;
    general_comment: string | null;
    created_at: string;
}

export interface WebsiteWithGrade extends Website {
    grades: WebsiteGrade | null;
}

export interface GradeSubmission {
    overall_aesthetic?: number;
    color_harmony?: number;
    typography_quality?: number;
    layout_spacing?: number;
    imagery_quality?: number;
    visual_hierarchy?: number;
    mobile_responsiveness?: number;
    notes?: Record<string, string>;
    general_comment?: string;
    is_designvorlage: boolean;
    is_good_lead: boolean;
}

export interface StackStats {
    ungraded_count: number;
    graded_count: number;
    designvorlage_count: number;
    good_lead_count: number;
}

export interface Stats {
    total_websites: number;
    total_comparisons: number;
    total_graded: number;
    total_designvorlage: number;
    total_good_leads: number;
    avg_elo: number;
}

export interface ScrapeConfig {
    location: string;
    radius_km: number;
    business_types: string[];
}

export interface ScrapeJob {
    id: number;
    location: string;
    radius_km: number;
    business_types: string[] | null;
    status: string;
    websites_found: number;
    error_message: string | null;
    created_at: string;
    completed_at: string | null;
}

export interface ComparisonPair {
    website_a: Website;
    website_b: Website;
}

export interface LeaderboardItem extends Website {
    rank: number;
}

// Grading field definitions
export const GRADING_FIELDS = [
    { key: 'overall_aesthetic', label: 'Overall Aesthetic', description: 'First impression, visual polish' },
    { key: 'color_harmony', label: 'Color Harmony', description: 'Color palette cohesion and appeal' },
    { key: 'typography_quality', label: 'Typography Quality', description: 'Font choices, readability, hierarchy' },
    { key: 'layout_spacing', label: 'Layout & Spacing', description: 'Whitespace usage, visual balance' },
    { key: 'imagery_quality', label: 'Imagery Quality', description: 'Photo/graphic quality and relevance' },
    { key: 'visual_hierarchy', label: 'Visual Hierarchy', description: 'Clear content prioritization' },
    { key: 'mobile_responsiveness', label: 'Mobile Responsiveness', description: 'Mobile-friendly design' },
] as const;

export type GradingFieldKey = typeof GRADING_FIELDS[number]['key'];

// --- Aggregation Types ---

export interface PlaceResult {
    rank: number;
    name: string;
    rating_count: number;
    rating_score: number | null;
    website_url: string | null;
    google_place_id: string;
}

export interface AggregationResponse {
    results: PlaceResult[];
    query: string;
    total_count: number;
    search_query_id: number;
}

