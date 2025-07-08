import azure.functions as func
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Dashboard function processed a request.')
        import os
        host = req.headers.get('host', 'your-function-app.azurewebsites.net')
        base_url = f"https://{host}/api"
        force_logo_url = os.environ.get('FORCE_LOGO_URL', '').strip()
        html_content = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>CoPPA Analytics Dashboard</title>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', Arial, sans-serif;
            font-size: 22px;
            margin: 0;
            padding: 40px;
            background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%);
            color: #232946;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(90deg, #fff 0%, #1e3a8a 100%);
            color: #1e3a8a;
            padding: 0 28px;
            margin-bottom: 40px;
            border-radius: 22px;
            box-shadow: 0 6px 32px rgba(30,58,138,0.13);
            position: relative;
            min-height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .dashboard-logo {{
            position: absolute;
            left: 40px;
            top: 50%;
            transform: translateY(-50%);
            height: 120px;
            width: auto;
            margin: 0;
            vertical-align: middle;
            display: block;
            flex-shrink: 0;
        }}
        .header-content {{
            position: absolute;
            left: 0;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            z-index: 1;
            pointer-events: none;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: bold;
            text-align: center;
            display: block;
            width: 100%;
        }}
        .header p {{
            margin: 8px 0 0 0;
            font-size: 1.3em;
            text-align: center;
            display: block;
            width: 100%;
        }}
        .container {{
            max-width: 1680px; /* Increased from 1280px */
            margin: 0 auto;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 36px; /* Increased gap */
            margin-bottom: 36px; /* Increased margin */
        }}
        .dashboard-grid-4 {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 36px; /* Increased gap */
            margin-bottom: 36px; /* Increased margin */
        }}
        .card {{
            background: rgba(255,255,255,0.95);
            border-radius: 22px; /* Slightly larger */
            padding: 44px 36px 36px 36px; /* Increased padding */
            box-shadow: 0 12px 40px rgba(30,58,138,0.13);
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .card:hover {{
            box-shadow: 0 16px 48px rgba(30,58,138,0.18);
            transform: translateY(-2px) scale(1.015);
        }}
        .metric {{
            text-align: center;
            padding: 22px; /* Increased padding */
        }}
        .metric-value {{
            font-size: 2.6em; /* Larger metric value */
            font-weight: bold;
            color: #1e3a8a;
        }}
        .metric-label {{
            color: #666;
            margin-top: 8px;
            font-size: 1.1em;
        }}
        .questions-list {{
            max-height: 520px; /* Increased height */
            overflow-y: auto;
        }}
        .question-item {{
            border-bottom: 1px solid #eee;
            padding: 16px 0; /* Increased padding */
        }}
        .question-text {{
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .question-meta {{
            font-size: 1em;
            color: #666;
        }}
        .controls {{
            background: white;
            padding: 28px; /* Increased padding */
            border-radius: 12px;
            margin-bottom: 28px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.10);
        }}
        .controls input, .controls select, .controls button {{
            margin: 8px;
            padding: 12px;
            font-size: 1.1em;
            border: 1px solid #ddd;
            border-radius: 6px;
        }}
        .controls button {{
            background-color: #1e3a8a;
            color: white;
            cursor: pointer;
        }}
        .loading {{
            text-align: center;
            padding: 28px;
            color: #666;
            font-size: 1.2em;
        }}
        .chart-container {{
            position: relative;
            height: 420px; /* Increased from 300px */
        }}
        .user-logo {{
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%);
            height: 120px;
            width: auto;
            margin: 0;
            vertical-align: middle;
            display: block;
            flex-shrink: 0;
            object-fit: contain;
            background: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/api/getlogo" alt="Logo" class="dashboard-logo">
            <div class="header-content">
                <h1>CoPPA Analytics Dashboard</h1>
                <p>Real Time Insights into User Interactions</p>
            </div>
            <img id="user-logo" src="{force_logo_url}" alt="User Logo" class="user-logo" onerror="this.style.display='none';document.getElementById('user-logo-placeholder').style.display='block';">
            <span id="user-logo-placeholder" style="display:none;position:absolute;right:40px;top:50%;transform:translateY(-50%);height:120px;width:120px;vertical-align:middle;">
                <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="60" cy="60" r="54" fill="#e5e7eb" stroke="#cbd5e1" stroke-width="6"/>
                  <text x="50%" y="54%" text-anchor="middle" fill="#94a3b8" font-size="32" font-family="Arial, sans-serif" dy=".3em">?</text>
                </svg>
            </span>
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
            <div class="dashboard-grid-4">
                <div class="card metric" style="background:#f0f8ff;">
                    <div class="metric-value" id="allTimeTotalQuestions">0</div>
                    <div class="metric-label">Total Questions (All-Time)</div>
                </div>
                <div class="card metric" style="background:#f0f8ff;">
                    <div class="metric-value" id="allTimeUniqueUsers">0</div>
                    <div class="metric-label">Unique Users (All-Time)</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="totalUserQuestions">0</div>
                    <div class="metric-label">Number of Questions in Selected Date Range</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="uniqueUsers">0</div>
                    <div class="metric-label">New Unique Users in Selected Date Range</div>
                </div>
            </div>
            <div class="dashboard-grid-4">
                <div class="card">
                    <h3>Top Conversation Themes</h3>
                    <div class="chart-container">
                        <canvas id="themesChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Recent Conversations by Theme</h3>
                    <div id="conversationTitlesByTheme"></div>
                </div>
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
                var themeLabels = data.themes.top_themes.map(function(theme) {{ return theme.theme; }});
                var themeCounts = data.themes.top_themes.map(function(theme) {{ return theme.count; }});
                var themeColors = [
                    '#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe',
                    '#f59e42', '#fbbf24', '#fde68a', '#fca5a5', '#f87171',
                    '#34d399', '#10b981', '#6ee7b7', '#a7f3d0', '#f472b6'
                ];
                var ctx = document.getElementById('themesChart').getContext('2d');
                if (window.themesChartInstance) {{ window.themesChartInstance.destroy(); }}
                window.themesChartInstance = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: themeLabels,
                        datasets: [{{
                            data: themeCounts,
                            backgroundColor: themeColors.slice(0, themeLabels.length)
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    font: {{ size: 20 }} // Increased font size for legend
                                }}
                            }}
                        }},
                        // Make chart labels larger
                        layout: {{ padding: 10 }},
                        elements: {{ arc: {{ borderWidth: 2 }} }},
                    }}
                }});
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
                    plugins: {{
                        legend: {{
                            labels: {{
                                font: {{ size: 20 }} // Increased font size for legend
                            }}
                        }},
                        title: {{ display: false }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ font: {{ size: 18 }} }} }},
                        y: {{ beginAtZero: true, ticks: {{ font: {{ size: 18 }} }} }}
                    }}
                }}
            }});
        }}
        async function loadQuestions() {{
            // Removed: No longer needed, recent questions update with dashboard
        }}
        // Show user logo on page load
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
