import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Website, GradeSubmission, StackStats, GradingFieldKey } from '../types';
import { GRADING_FIELDS } from '../types';
import './StackReview.css';

const LIKERT_LABELS = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];

interface LikertSliderProps {
    fieldKey: GradingFieldKey;
    label: string;
    description: string;
    value: number | null;
    note: string;
    onChange: (value: number | null) => void;
    onNoteChange: (note: string) => void;
}

function LikertSlider({ label, description, value, note, onChange, onNoteChange }: LikertSliderProps) {
    return (
        <div className="likert-field">
            <div className="likert-header">
                <label>{label}</label>
                <span className="likert-description">{description}</span>
            </div>
            <div className="likert-scale">
                {[1, 2, 3, 4, 5].map((n) => (
                    <button
                        key={n}
                        className={`likert-btn ${value === n ? 'active' : ''}`}
                        onClick={() => onChange(value === n ? null : n)}
                        title={LIKERT_LABELS[n - 1]}
                    >
                        {n}
                    </button>
                ))}
                <span className="likert-label">{value ? LIKERT_LABELS[value - 1] : '—'}</span>
            </div>
            <input
                type="text"
                className="note-input"
                placeholder="Add note for taxonomy..."
                value={note}
                onChange={(e) => onNoteChange(e.target.value)}
            />
        </div>
    );
}

export function StackReview() {
    const [website, setWebsite] = useState<Website | null>(null);
    const [stats, setStats] = useState<StackStats | null>(null);
    const [grades, setGrades] = useState<Record<GradingFieldKey, number | null>>({
        overall_aesthetic: null,
        color_harmony: null,
        typography_quality: null,
        layout_spacing: null,
        imagery_quality: null,
        visual_hierarchy: null,
        mobile_responsiveness: null,
    });
    const [notes, setNotes] = useState<Record<string, string>>({});
    const [generalComment, setGeneralComment] = useState('');
    const [isDesignvorlage, setIsDesignvorlage] = useState(false);
    const [isGoodLead, setIsGoodLead] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadNext = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const [nextWebsite, stackStats] = await Promise.all([
                api.getNextUngraded(),
                api.getStackStats(),
            ]);
            setWebsite(nextWebsite);
            setStats(stackStats);
            // Reset form
            setGrades({
                overall_aesthetic: null,
                color_harmony: null,
                typography_quality: null,
                layout_spacing: null,
                imagery_quality: null,
                visual_hierarchy: null,
                mobile_responsiveness: null,
            });
            setNotes({});
            setGeneralComment('');
            setIsDesignvorlage(false);
            setIsGoodLead(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadNext();
    }, []);

    const handleSubmit = async () => {
        if (!website) return;

        setIsSubmitting(true);
        setError(null);

        const submission: GradeSubmission = {
            overall_aesthetic: grades.overall_aesthetic ?? undefined,
            color_harmony: grades.color_harmony ?? undefined,
            typography_quality: grades.typography_quality ?? undefined,
            layout_spacing: grades.layout_spacing ?? undefined,
            imagery_quality: grades.imagery_quality ?? undefined,
            visual_hierarchy: grades.visual_hierarchy ?? undefined,
            mobile_responsiveness: grades.mobile_responsiveness ?? undefined,
            notes: Object.fromEntries(Object.entries(notes).filter(([_, v]) => v)),
            general_comment: generalComment || undefined,
            is_designvorlage: isDesignvorlage,
            is_good_lead: isGoodLead,
        };

        try {
            await api.gradeWebsite(website.id, submission);
            await loadNext();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to submit');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleSkip = async () => {
        if (!website) return;

        setIsSubmitting(true);
        try {
            await api.skipWebsite(website.id);
            await loadNext();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to skip');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return <div className="stack-review loading">Loading...</div>;
    }

    if (!website) {
        return (
            <div className="stack-review empty">
                <div className="empty-state">
                    <h2>🎉 All caught up!</h2>
                    <p>No more websites to review.</p>
                    {stats && (
                        <div className="stats-summary">
                            <span>✅ {stats.graded_count} graded</span>
                            <span>🎨 {stats.designvorlage_count} Designvorlagen</span>
                            <span>🎯 {stats.good_lead_count} Good Leads</span>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="stack-review">
            {/* Stats Bar */}
            {stats && (
                <div className="stats-bar">
                    <span className="stat">
                        📋 <strong>{stats.ungraded_count}</strong> remaining
                    </span>
                    <span className="stat">
                        ✅ <strong>{stats.graded_count}</strong> graded
                    </span>
                    <span className="stat">
                        🎨 <strong>{stats.designvorlage_count}</strong> Designvorlagen
                    </span>
                    <span className="stat">
                        🎯 <strong>{stats.good_lead_count}</strong> Good Leads
                    </span>
                </div>
            )}

            <div className="review-container">
                {/* Website Preview */}
                <div className="preview-section">
                    <div className="website-info">
                        <h2>{website.name || 'Unnamed Website'}</h2>
                        <a href={website.url} target="_blank" rel="noopener noreferrer" className="website-url">
                            {website.url}
                        </a>
                        {website.business_type && (
                            <span className="business-type">{website.business_type}</span>
                        )}
                        {website.address && (
                            <span className="address">{website.address}</span>
                        )}
                    </div>
                    <div className="iframe-container">
                        <iframe
                            src={website.url}
                            title="Website Preview"
                            sandbox="allow-scripts allow-same-origin"
                        />
                    </div>
                </div>

                {/* Grading Form */}
                <div className="grading-section">
                    <h3>Visual Assessment</h3>

                    {error && <div className="error-message">{error}</div>}

                    <div className="likert-fields">
                        {GRADING_FIELDS.map((field) => (
                            <LikertSlider
                                key={field.key}
                                fieldKey={field.key}
                                label={field.label}
                                description={field.description}
                                value={grades[field.key]}
                                note={notes[field.key] || ''}
                                onChange={(value) => setGrades({ ...grades, [field.key]: value })}
                                onNoteChange={(note) => setNotes({ ...notes, [field.key]: note })}
                            />
                        ))}
                    </div>

                    <div className="general-comment">
                        <label>General Notes</label>
                        <textarea
                            placeholder="Any additional observations..."
                            value={generalComment}
                            onChange={(e) => setGeneralComment(e.target.value)}
                            rows={3}
                        />
                    </div>

                    {/* Flag Buttons */}
                    <div className="flag-buttons">
                        <button
                            className={`flag-btn designvorlage ${isDesignvorlage ? 'active' : ''}`}
                            onClick={() => setIsDesignvorlage(!isDesignvorlage)}
                        >
                            🎨 Designvorlage
                        </button>
                        <button
                            className={`flag-btn good-lead ${isGoodLead ? 'active' : ''}`}
                            onClick={() => setIsGoodLead(!isGoodLead)}
                        >
                            🎯 Good Lead
                        </button>
                    </div>

                    {/* Action Buttons */}
                    <div className="action-buttons">
                        <button
                            className="skip-btn"
                            onClick={handleSkip}
                            disabled={isSubmitting}
                        >
                            Skip
                        </button>
                        <button
                            className="submit-btn"
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Saving...' : 'Submit & Next'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
