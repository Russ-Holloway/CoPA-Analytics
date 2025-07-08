import azure.functions as func
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Dashboard function processed a request.')
        host = req.headers.get('host', 'your-function-app.azurewebsites.net')
        base_url = f"https://{host}/api"
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoPPA Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', Arial, sans-serif;
            font-size: 18px;
            margin: 0;
            padding: 32px;
            background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%);
            color: #232946;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(90deg, #6366f1 0%, #1e3a8a 100%);
            color: #fff;
            padding: 32px 20px 24px 20px;
            text-align: center;
            margin-bottom: 32px;
            border-radius: 18px;
            box-shadow: 0 4px 24px rgba(30,58,138,0.10);
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 28px;
            margin-bottom: 28px;
        }}
        .card {{
            background: rgba(255,255,255,0.95);
            border-radius: 18px;
            padding: 32px 26px 26px 26px;
            box-shadow: 0 8px 32px rgba(30,58,138,0.13);
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .card:hover {{
            box-shadow: 0 12px 40px rgba(30,58,138,0.18);
            transform: translateY(-2px) scale(1.01);
        }}
        .metric {{
            text-align: center;
            padding: 15px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #1e3a8a;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .questions-list {{
            max-height: 400px;
            overflow-y: auto;
        }}
        .question-item {{
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }}
        .question-text {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .question-meta {{
            font-size: 0.9em;
            color: #666;
        }}
        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .controls input, .controls select, .controls button {{
            margin: 5px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .controls button {{
            background-color: #1e3a8a;
            color: white;
            cursor: pointer;
        }}
        .loading {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CoPPA Analytics Dashboard</h1>
            <p>Real Time Insights into User Interactions</p>
        </div>
        <div class="controls">
            <label>Start Date: <input type="date" id="startDate"></label>
            <label>End Date: <input type="date" id="endDate"></label>
            <label>Conversation:
                <select id="category" onchange="loadData()">
                    <option value="all">All Conversation Themes</option>
                </select>
            </label>
            <button onclick="loadData()">Update Dashboard</button>
        </div>
        <div id="loading" class="loading">Loading dashboard data...</div>
        <div id="dashboard" style="display: none;">
            <div class="grid" style="grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 0;">
                <div class="card metric" style="background:#f0f8ff;">
                    <div class="metric-value" id="allTimeTotalQuestions">0</div>
                    <div class="metric-label">Total Questions (All-Time)</div>
                </div>
                <div class="card metric" style="background:#f0f8ff;">
                    <div class="metric-value" id="allTimeUniqueUsers">0</div>
                    <div class="metric-label">Unique Users (All-Time)</div>
                </div>
            </div>
            <div class="grid" style="grid-template-columns: repeat(2, 1fr); gap: 24px; margin-top: 12px; margin-bottom: 28px;">
                <div class="card metric">
                    <div class="metric-value" id="totalUserQuestions">0</div>
                    <div class="metric-label">Number of Questions in Selected Date Range</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="uniqueUsers">0</div>
                    <div class="metric-label">New Unique Users in Selected Date Range</div>
                </div>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Conversations Breakdown</h3>
                    <div class="chart-container">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Top Conversation Themes</h3>
                    <div id="themes"></div>
                </div>
                <div class="card">
                    <h3>Recent Conversations by Theme</h3>
                    <div id="conversationTitlesByTheme"></div>
                </div>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Hourly Distribution</h3>
                    <div class="chart-container">
                        <canvas id="hourlyChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Recent Conversations</h3>
                    <div id="questions" class="questions-list"></div>
                </div>
            </div>
        </div>
    </div>
    <script>
        const baseUrl = '{base_url}';
        let categoryChart, hourlyChart;
        function setDefaultDates() {{
            const today = new Date();
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = weekAgo.toISOString().split('T')[0];
        }}
        async function loadData() {{
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const theme = document.getElementById('category').value;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            try {{
                let url = `${{baseUrl}}/GetAnalytics`;
                const params = new URLSearchParams();
                if (startDate) params.append('startDate', startDate + 'T00:00:00Z');
                if (endDate) params.append('endDate', endDate + 'T23:59:59Z');
                if (theme !== 'all') params.append('theme', theme);
                if (params.toString()) url += '?' + params.toString();
                const response = await fetch(url);
                const data = await response.json();
                updateDashboard(data);
            }} catch (error) {{
                console.error('Error loading data:', error);
                document.getElementById('loading').innerHTML = 'Error loading data: ' + error.message;
            }}
        }}
        // Populate the dropdown with conversation themes from the themes box after dashboard loads
        function updateThemeDropdown(data) {{
            if (data.themes && data.themes.top_themes) {{
                const categorySelect = document.getElementById('category');
                const current = categorySelect.value;
                categorySelect.innerHTML = '<option value="all">All Conversation Themes</option>';
                data.themes.top_themes.forEach(t => {{
                    const opt = document.createElement('option');
                    opt.value = t.theme;
                    opt.textContent = t.theme.charAt(0).toUpperCase() + t.theme.slice(1);
                    if (t.theme === current) opt.selected = true;
                    categorySelect.appendChild(opt);
                }});
            }}
        }}
        function updateDashboard(data) {{
            // All-time metrics (NEW)
            document.getElementById('allTimeTotalQuestions').textContent = data.allTime?.totalQuestions ?? 'N/A';
            document.getElementById('allTimeUniqueUsers').textContent = data.allTime?.uniqueUsers ?? 'N/A';
            // Existing filtered metrics
            document.getElementById('uniqueUsers').textContent = data.summary?.uniqueUsers || 0;
            document.getElementById('totalUserQuestions').textContent = data.summary?.totalUserQuestions || 0;
            // Top Conversation Themes
            if (data.themes?.top_themes) {{
                const themesHtml = data.themes.top_themes.map(theme =>
                    `<div style="padding: 5px 0; border-bottom: 1px solid #eee;">
                        <strong>${{theme.theme}}</strong>: ${{theme.count}} times
                    </div>`
                ).join('');
                document.getElementById('themes').innerHTML = themesHtml;
                updateThemeDropdown(data);
            }}
            // --- Additional: Recent Conversations by Theme ---
            if (data.themes && data.themes.top_themes && data.questions && data.questions.recent) {{
                var themeToRecent = {{}};
                for (var i = 0; i < data.themes.top_themes.length; i++) {{
                    var theme = data.themes.top_themes[i].theme;
                    for (var j = 0; j < data.questions.recent.length; j++) {{
                        var q = data.questions.recent[j];
                        if (Array.isArray(q.themes) && q.themes.indexOf(theme) !== -1) {{
                            if (!themeToRecent[theme]) themeToRecent[theme] = q;
                        }}
                    }}
                }}
                var byThemeHtml = Object.keys(themeToRecent).map(function(theme) {{
                    var q = themeToRecent[theme];
                    return `<div style='padding:5px 0; border-bottom:1px solid #eee;'><a href='/api/conversation?title=${{encodeURIComponent(q.title || '')}}' target='_blank' style='text-decoration:underline;color:#1e3a8a;cursor:pointer;'><strong>` + theme.charAt(0).toUpperCase() + theme.slice(1) + `</strong></a>: ` + (q.title || '(No title)') + ` <span style='color:#888;font-size:0.9em;'>(` + (q.createdAt ? new Date(q.createdAt).toLocaleString() : '') + `)</span></div>`;
                }}).join('');
                var container = document.getElementById('conversationTitlesByTheme');
                if (container) container.innerHTML = byThemeHtml || '<em>No data</em>';
            }}
            if (data.categories) {{
                updateCategoryChart(data.categories);
            }}
            if (data.trends?.hourly_distribution) {{
                updateHourlyChart(data.trends.hourly_distribution);
            }}
            if (data.questions?.recent) {{
                var questionsHtml = '';
                for (var i = 0; i < data.questions.recent.length; i++) {{
                    var q = data.questions.recent[i];
                    var titleHtml = 'No question recorded';
                    if (q && q.title) titleHtml = '<a href="/api/conversationviewtitle?title=' + encodeURIComponent(q.title) + '" target="_blank" style="color:#1e3a8a;text-decoration:underline;">' + q.title + '</a>';
                    var date = q && q.createdAt ? new Date(q.createdAt).toLocaleString() : '';
                    var category = q && q.category ? q.category : '';
                    questionsHtml = questionsHtml + '<div class="question-item">' +
                        '<div class="question-text">' + titleHtml + '</div>' +
                        '<div class="question-meta">Category: ' + category + ' | ' + date + '</div>' +
                    '</div>';
                }}
                document.getElementById('questions').innerHTML = questionsHtml;
            }}
            document.getElementById('loading').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
        }}
        function updateCategoryChart(categories) {{
            const ctx = document.getElementById('categoryChart').getContext('2d');
            if (categoryChart) {{
                categoryChart.destroy();
            }}
            const labels = Object.keys(categories);
            const counts = labels.map(label => categories[label].count);
            categoryChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: counts,
                        backgroundColor: [
                            '#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }});
        }}
        function updateHourlyChart(hourlyData) {{
            const ctx = document.getElementById('hourlyChart').getContext('2d');
            if (hourlyChart) {{
                hourlyChart.destroy();
            }}
            const hours = Array.from({{length: 24}}, (_, i) => i + ':00');
            hourlyChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: hours,
                    datasets: [{{
                        label: 'Interactions',
                        data: hourlyData,
                        backgroundColor: '#1e3a8a'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}
        async function loadQuestions() {{
            // Removed: No longer needed, recent questions update with dashboard
        }}
        setDefaultDates();
        loadData();
    </script>
</body>
</html>
        """
        return func.HttpResponse(
            html_content,
            status_code=200,
            headers={"Content-Type": "text/html"}
        )
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        return func.HttpResponse(
            f"Dashboard error: {str(e)}",
            status_code=500,
            headers={"Content-Type": "text/plain"}
        )
