// ===========================
// TAB NAVIGATION
// ===========================
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
});

// Character counter
const draftEl = document.getElementById('post-draft');
draftEl.addEventListener('input', () => {
    document.getElementById('draft-count').textContent = draftEl.value.length;
});

// State
let currentRewrittenText = '';


// ===========================
// FEATURE 1: POST TO X
// ===========================

async function rewritePost() {
    const text = draftEl.value.trim();
    if (!text) return alert('Please enter a draft first.');

    const btn = document.getElementById('btn-rewrite');
    btn.disabled = true;
    btn.textContent = '⏳ Rewriting...';

    try {
        const res = await fetch('/api/rewrite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
    draftEl.focus();
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
            headers: { 'Content-Type': 'application/json' },
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
            headers: { 'Content-Type': 'application/json' },
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

    // Safety check for all fields
    const safeGet = (obj, path, def = {}) => {
        return path.split('.').reduce((acc, part) => acc && acc[part], obj) || def;
    };

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


function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
