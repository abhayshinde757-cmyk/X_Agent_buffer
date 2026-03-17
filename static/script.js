// ==========================================
// 🚀 X COMMAND CENTER - CORE LOGIC
// ==========================================

console.log("🚀 X Command Center script loaded!");

// --- 1. GLOBALLY EXPOSED FUNCTIONS (Fixed for Brave/Chrome) ---
window.syncExcel = syncExcel;
window.confirmExcelPost = confirmExcelPost;
window.rewritePost = rewritePost;
window.publishPost = publishPost;
window.runAnalytics = runAnalytics;
window.editDraft = editDraft;

// State
let currentRewrittenText = '';

// Helper
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// ===========================
// FEATURE 1: POST TO X
// ===========================

async function rewritePost() {
    const draftEl = document.getElementById('post-draft');
    const text = draftEl.value.trim();
    if (!text) return alert('Please enter a draft first.');

    const btn = document.getElementById('btn-rewrite');
    btn.disabled = true;
    btn.textContent = '⏳ Rewriting...';

    try {
        const res = await fetch('/api/rewrite', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify({ text })
        });
        const data = await res.json();

        const resultBox = document.getElementById('rewrite-result');
        const resultText = document.getElementById('rewritten-text');
        const countEl = document.getElementById('rewritten-count');

        if (data.success) {
            currentRewrittenText = data.rewritten;
            resultText.textContent = data.rewritten;
            countEl.textContent = data.char_count + ' / 280 characters';
            resultBox.className = 'result-box visible success';
            document.getElementById('publish-section').style.display = 'block';
        } else {
            resultText.textContent = 'Error: ' + data.error;
            resultBox.className = 'result-box visible error';
        }
    } catch (e) {
        alert('Network error: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '✨ AI Rewrite';
    }
}

function editDraft() {
    document.getElementById('publish-section').style.display = 'none';
    document.getElementById('rewrite-result').className = 'result-box';
    document.getElementById('post-result').className = 'result-box';
    document.getElementById('post-draft').focus();
}

async function publishPost() {
    if (!currentRewrittenText) return alert('Please rewrite your draft first.');

    const imageUrl = document.getElementById('image-url').value.trim();
    const btn = document.getElementById('btn-publish');
    const spinner = document.getElementById('post-spinner');
    const resultBox = document.getElementById('post-result');
    const resultText = document.getElementById('post-result-text');

    btn.disabled = true;
    spinner.classList.add('visible');
    resultBox.className = 'result-box';

    try {
        const body = { text: currentRewrittenText };
        if (imageUrl) body.image_url = imageUrl;

        const res = await fetch('/api/post', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        if (data.success) {
            resultText.innerHTML = `
                <div style="margin-bottom:0.5rem;">✅ <strong>Post created successfully!</strong></div>
                <div style="margin-bottom:0.3rem;">Buffer ID: <code>${data.post_id}</code></div>
                <div>Twitter Link: <a href="${data.twitter_link}" target="_blank" class="result-link">${data.twitter_link}</a></div>
            `;
            resultBox.className = 'result-box visible success';
        } else {
            resultText.textContent = 'Error: ' + data.error;
            resultBox.className = 'result-box visible error';
        }
    } catch (e) {
        resultText.textContent = 'Network error: ' + e.message;
        resultBox.className = 'result-box visible error';
    } finally {
        btn.disabled = false;
        spinner.classList.remove('visible');
    }
}

// ===========================
// FEATURE 2 & 3: ANALYTICS + AI Q/A
// ===========================

async function runAnalytics() {
    const query = document.getElementById('search-query').value.trim();
    if (!query) return alert('Please enter a hashtag or account.');

    const btn = document.getElementById('btn-scrape');
    const spinner = document.getElementById('scrape-spinner');
    const resultsDiv = document.getElementById('analytics-results');
    const errorBox = document.getElementById('scrape-error');

    btn.disabled = true;
    spinner.classList.add('visible');
    resultsDiv.style.display = 'none';
    errorBox.className = 'result-box';

    try {
        const res = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        if (data.success) {
            renderAnalytics(data.data);
            resultsDiv.style.display = 'block';
        } else {
            errorBox.querySelector('.result-text')?.remove();
            errorBox.innerHTML = `<div class="result-label">Error</div><div class="result-text">${data.error}</div>`;
            errorBox.className = 'result-box visible error';
        }
    } catch (e) {
        errorBox.innerHTML = `<div class="result-label">Error</div><div class="result-text">Network error: ${e.message}</div>`;
        errorBox.className = 'result-box visible error';
    } finally {
        btn.disabled = false;
        spinner.classList.remove('visible');
    }
}

function renderAnalytics(data) {
    if (!data || !data.analytics) return;
    const a = data.analytics;

    // Stats Grid
    const statsGrid = document.getElementById('stats-grid');
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${a.buzz.total_posts}</div>
            <div class="stat-label">Total Posts Scraped</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${a.buzz.unique_contributors}</div>
            <div class="stat-label">Unique Contributors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${a.questions.count}</div>
            <div class="stat-label">Questions Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${a.photos.count}</div>
            <div class="stat-label">Posts With Photos</div>
        </div>
    `;

    // Sentiment
    const sentimentSec = document.getElementById('sentiment-section');
    sentimentSec.innerHTML = `
        <div class="section-title">Sentiment Analysis</div>
        <div class="sentiment-bar">
            <div class="sentiment-positive" style="width:${a.sentiment.positive}%"></div>
            <div class="sentiment-negative" style="width:${a.sentiment.negative}%"></div>
            <div class="sentiment-neutral" style="width:${a.sentiment.neutral}%"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--text-muted);">
            <span>🟢 Positive: ${a.sentiment.positive}%</span>
            <span>🔴 Negative: ${a.sentiment.negative}%</span>
            <span>⚪ Neutral: ${a.sentiment.neutral}%</span>
        </div>
    `;

    // Trending
    const trendingSec = document.getElementById('trending-section');
    let trendHTML = '<div class="section-title">Trending Topics</div>';
    if (a.trending.items.length > 0) {
        a.trending.items.forEach(t => {
            trendHTML += `<div class="trend-item"><span class="trend-word">${t.word}</span><span class="trend-count">${t.count}</span></div>`;
        });
    } else {
        trendHTML += '<p style="color:var(--text-muted);font-size:0.9rem;">No trending topics found.</p>';
    }
    trendingSec.innerHTML = trendHTML;

    // Top Engaged
    const engagedSec = document.getElementById('engaged-section');
    let engagedHTML = '<div class="section-title">🔥 Top Engaged Tweets</div>';
    if (a.top_engaged.items.length > 0) {
        a.top_engaged.items.forEach(t => {
            engagedHTML += `
                <div class="tweet-item">
                    <div class="tweet-text">${escapeHtml(t.text)}</div>
                    <div class="tweet-meta">
                        <span>❤️ ${t.likes}</span>
                        <span>🔄 ${t.reposts}</span>
                        <span>💬 ${t.replies}</span>
                        ${t.url !== 'Unknown' ? `<a href="${t.url}" target="_blank">View →</a>` : ''}
                    </div>
                </div>
            `;
        });
    } else {
        engagedHTML += '<p style="color:var(--text-muted);font-size:0.9rem;">No engagement data found.</p>';
    }
    engagedSec.innerHTML = engagedHTML;

    // Questions
    const questionsSec = document.getElementById('questions-section');
    let qHTML = '<div class="section-title">❓ Questions From Audience</div>';
    if (a.questions.items.length > 0) {
        a.questions.items.forEach(q => {
            qHTML += `
                <div class="tweet-item">
                    <div class="tweet-text">${escapeHtml(q.text)}</div>
                    <div class="tweet-meta">
                        ${q.url !== 'Unknown' ? `<a href="${q.url}" target="_blank">View →</a>` : ''}
                    </div>
                </div>
            `;
        });
    } else {
        qHTML += '<p style="color:var(--text-muted);font-size:0.9rem;">No questions detected.</p>';
    }
    questionsSec.innerHTML = qHTML;

    // Advocates
    const advocatesSec = document.getElementById('advocates-section');
    let advHTML = '<div class="section-title">Event Advocates</div>';
    if (a.advocates.items.length > 0) {
        a.advocates.items.forEach(u => {
            advHTML += `<div class="trend-item"><span class="trend-word">${escapeHtml(u.user)}</span><span class="trend-count">${u.count} tweets</span></div>`;
        });
    } else {
        advHTML += '<p style="color:var(--text-muted);font-size:0.9rem;">No advocate data.</p>';
    }
    advocatesSec.innerHTML = advHTML;

    // AI Insights
    const aiSec = document.getElementById('ai-section');
    aiSec.innerHTML = `
        <div class="section-title">🧠 AI Deep Analysis & Q/A</div>
        <div class="ai-insights">${escapeHtml(data.ai_insights)}</div>
    `;
}

// ===========================
// FEATURE 4: EXCEL MASTER AGENT (Triggered Sync)
// ===========================

async function syncExcel() {
    const btn = document.getElementById('btn-sync-excel');
    const container = document.getElementById('excel-results-container');
    const errorBox = document.getElementById('excel-error');
    const syncStatus = document.getElementById('sync-status');

    btn.disabled = true;
    btn.textContent = '⏳ Syncing Remote Excel...';
    container.style.opacity = '0.5';

    try {
        const res = await fetch('/api/excel/sync', {
            headers: { 'Cache-Control': 'no-cache' }
        });
        const data = await res.json();

        if (data.success) {
            errorBox.style.display = 'none';
            if (data.events.length === 0) {
                container.innerHTML = '<p style="text-align:center;color:var(--text-muted);margin-top:2rem;">No events waiting for review.</p>';
                if (syncStatus) syncStatus.textContent = 'Last checked: ' + new Date().toLocaleTimeString() + ' (No new events)';
            } else {
                renderExcelDrafts(data.events);
                if (syncStatus) syncStatus.textContent = 'Last sync: ' + new Date().toLocaleTimeString() + ` (${data.events.length} pending review)`;
            }
        } else {
            console.error('Sync Error:', data.error);
            alert('Sync failed: ' + data.error);
        }
    } catch (e) {
        console.error('Sync Network Error:', e.message);
        alert('Network error during sync.');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Sync Now';
        container.style.opacity = '1';
    }
}

function renderExcelDrafts(events) {
    const container = document.getElementById('excel-results-container');
    let html = '<div class="section-title">Events Awaiting Review</div>';

    events.forEach(ev => {
        html += `
            <div class="card excel-card" id="excel-card-${ev.index}">
                <div class="excel-header">
                    <div>
                        <div class="excel-title">${escapeHtml(ev['event title'])}</div>
                        <div class="excel-meta">${escapeHtml(ev.location)} | ${escapeHtml(ev.time)}</div>
                    </div>
                    <div class="status-badge">READY FOR REVIEW</div>
                </div>

                <div class="excel-widgets">
                    <div class="excel-widget ai-post-widget">
                        <div class="widget-label">✨ AI Elaborated Post</div>
                        <textarea id="excel-draft-${ev.index}" class="excel-textarea">${ev.ai_draft}</textarea>
                    </div>

                    <div class="excel-widget image-link-widget">
                        <div class="widget-label">🖼️ Poster Image Link</div>
                        <div class="image-link-box">
                            <input type="text" readonly value="${ev.posterlink || 'No image linked'}" class="excel-input-readonly">
                            ${ev.posterlink ? `<a href="${ev.posterlink}" target="_blank" class="widget-link">View Original →</a>` : ''}
                        </div>
                    </div>
                </div>

                <div class="btn-row">
                    <button class="btn btn-primary" onclick="confirmExcelPost(${ev.index}, '${ev.posterlink || ''}')">🚀 Finalize & Publish</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function confirmExcelPost(index, imageUrl) {
    const text = document.getElementById(`excel-draft-${index}`).value.trim();
    if (!text) return alert('Post text cannot be empty.');

    if (!confirm("Confirm posting this event to X?")) return;

    const card = document.getElementById(`excel-card-${index}`);
    const btn = card.querySelector('button');
    btn.disabled = true;
    btn.textContent = '⏳ Publishing...';

    try {
        const res = await fetch('/api/excel/confirm', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify({ index, text, image_url: imageUrl })
        });
        const data = await res.json();

        if (data.success) {
            card.innerHTML = `
                <div class="excel-header">
                    <div class="excel-title">✅ Successfully Posted</div>
                </div>
                <div class="result-text success" style="margin-top:1rem;">
                    X Post URL: <a href="${data.link}" target="_blank" class="result-link">${data.link}</a>
                </div>
            `;
            setTimeout(() => {
                card.remove();
                if (document.querySelectorAll('.excel-card').length === 0) {
                     document.getElementById('excel-results-container').innerHTML = '<p style="text-align:center;color:var(--text-muted);margin-top:2rem;">All events published!</p>';
                }
            }, 3000);
        } else {
            alert('Error: ' + data.error);
            btn.disabled = false;
            btn.textContent = '🚀 Finalize & Publish';
        }
    } catch (e) {
        alert('Network error: ' + e.message);
        btn.disabled = false;
        btn.textContent = '🚀 Finalize & Publish';
    }
}

// --- DOM EVENT LISTENERS (Initialize UI) ---
document.addEventListener('DOMContentLoaded', () => {
    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    // Character counter
    const draftInput = document.getElementById('post-draft');
    if (draftInput) {
        draftInput.addEventListener('input', () => {
            document.getElementById('draft-count').textContent = draftInput.value.length;
        });
    }
});
