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
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #1e3a8a;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            <label>Category:
                <select id="category">
                    <option value="all">All Categories</option>
                    <option value="crime_reporting">Crime Reporting</option>
                    <option value="traffic_incidents">Traffic Incidents</option>
                    <option value="general_enquiry">General Enquiry</option>
                    <option value="lost_property">Lost Property</option>
                    <option value="noise_complaints">Noise Complaints</option>
                </select>
            </label>
            <button onclick="loadData()">Update Dashboard</button>
            <button onclick="loadQuestions()">Load Recent Questions</button>
        </div>
        <div id="loading" class="loading">Loading dashboard data...</div>
        <div id="dashboard" style="display: none;">
            <div class="grid">
                <div class="card metric">
                    <div class="metric-value" id="totalInteractions">0</div>
                    <div class="metric-label">Total Interactions</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="uniqueUsers">0</div>
                    <div class="metric-label">Unique Users</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="avgResponseTime">0s</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Categories Breakdown</h3>
                    <div class="chart-container">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Top Themes</h3>
                    <div id="themes"></div>
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
                    <h3>Recent Questions</h3>
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
            const category = document.getElementById('category').value;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            try {{
                let url = `${{baseUrl}}/GetAnalytics`;
                const params = new URLSearchParams();
                if (startDate) params.append('startDate', startDate + 'T00:00:00Z');
                if (endDate) params.append('endDate', endDate + 'T23:59:59Z');
                if (category !== 'all') params.append('category', category);
                if (params.toString()) url += '?' + params.toString();
                const response = await fetch(url);
                const data = await response.json();
                updateDashboard(data);
            }} catch (error) {{
                console.error('Error loading data:', error);
                document.getElementById('loading').innerHTML = 'Error loading data: ' + error.message;
            }}
        }}
        function updateDashboard(data) {{
            document.getElementById('totalInteractions').textContent = data.summary?.totalInteractions || 0;
            document.getElementById('uniqueUsers').textContent = data.summary?.uniqueUsers || 0;
            // Format avg response time as h:mm:ss or m:ss or s
            let avgSec = data.summary?.avgResponseTimeSeconds;
            let formatted = 'N/A';
            if (typeof avgSec === 'number' && !isNaN(avgSec)) {{
                let sec = Math.floor(avgSec % 60);
                let min = Math.floor((avgSec / 60) % 60);
                let hr = Math.floor(avgSec / 3600);
                if (hr > 0) {{
                    formatted = `${{hr}}h ${{min}}m ${{sec}}s`;
                }} else if (min > 0) {{
                    formatted = `${{min}}m ${{sec}}s`;
                }} else {{
                    formatted = `${{sec}}s`;
                }}
            }}
            document.getElementById('avgResponseTime').textContent = formatted;
            if (data.themes?.top_themes) {{
                const themesHtml = data.themes.top_themes.map(theme =>
                    `<div style="padding: 5px 0; border-bottom: 1px solid #eee;">
                        <strong>${{theme.theme}}</strong>: ${{theme.count}} times
                    </div>`
                ).join('');
                document.getElementById('themes').innerHTML = themesHtml;
            }}
            if (data.categories) {{
                updateCategoryChart(data.categories);
            }}
            if (data.trends?.hourly_distribution) {{
                updateHourlyChart(data.trends.hourly_distribution);
            }}
            if (data.questions?.recent) {{
                const questionsHtml = data.questions.recent.map(q =>
                    `<div class="question-item" style="cursor:pointer;" onclick="showConversation('${q.id}')">
                        <div class="question-text">${q.title || 'No question recorded'}</div>
                        <div class="question-meta">
                            Category: ${q.category} |
                            ${q.createdAt ? new Date(q.createdAt).toLocaleString() : ''}
                            ${q.themes && q.themes.length ? ' | Themes: ' + q.themes.join(', ') : ''}
                            ${typeof q.responseTimeSeconds === 'number' ? ' | Response: ' + Math.round(q.responseTimeSeconds) + 's' : ''}
                        </div>
                    </div>`
                ).join('');
                document.getElementById('questions').innerHTML = questionsHtml;
            }}
            // Hide chat modal if open
            if (typeof hideChatModal === 'function') hideChatModal();
            document.getElementById('loading').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
        }}

        // Chat modal
        function showConversation(conversationId) {{
            fetch(`${baseUrl}/GetConversation?conversationId=${conversationId}`)
                .then(resp => resp.json())
                .then(data => {{
                    if (!data.conversation) return;
                    let html = '<div style="max-height:60vh;overflow-y:auto;padding:10px;">';
                    data.conversation.forEach(msg => {{
                        let who = msg.type === 'conversation' ? 'User' : (msg.role === 'tool' ? 'AI' : (msg.role || msg.type));
                        let time = msg.createdAt ? new Date(msg.createdAt).toLocaleString() : '';
                        let content = msg.title || msg.question || msg.content || '';
                        if (typeof content === 'string' && content.startsWith('{')) {{
                            try {{ content = JSON.parse(content).text || content; }} catch(e) {{}}
                        }}
                        html += `<div style="margin-bottom:10px;"><b>${who}</b> <span style="color:#888;font-size:0.9em;">${time}</span><div style="margin-left:10px;">${content}</div></div>`;
                    }});
                    html += '</div>';
                    document.getElementById('chatModalContent').innerHTML = html;
                    document.getElementById('chatModal').style.display = 'block';
                }});
        }}
        function hideChatModal() {{
            const modal = document.getElementById('chatModal');
            if (modal) modal.style.display = 'none';
        }}
    </script>
    <div id="chatModal" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center;">
        <div style="background:white;max-width:600px;margin:40px auto;padding:20px;border-radius:8px;position:relative;">
            <button onclick="hideChatModal()" style="position:absolute;top:10px;right:10px;">Close</button>
            <h3>Conversation</h3>
            <div id="chatModalContent"></div>
        </div>
    </div>
    <script>
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
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const category = document.getElementById('category').value;
            try {{
                let url = `${{baseUrl}}/GetQuestions`;
                const params = new URLSearchParams();
                if (startDate) params.append('startDate', startDate + 'T00:00:00Z');
                if (endDate) params.append('endDate', endDate + 'T23:59:59Z');
                if (category !== 'all') params.append('category', category);
                params.append('limit', '20');
                if (params.toString()) url += '?' + params.toString();
                const response = await fetch(url);
                const data = await response.json();
                if (data.questions) {{
                    const questionsHtml = data.questions.map(q =>
                        `<div class="question-item">
                            <div class="question-text">${{q.title || '(No title)'}} </div>
                            <div class="question-meta">
                                ID: ${{q.id}} | Type: ${{q.type}} | User: ${{q.userId}} | Created: ${{q.createdAt ? new Date(q.createdAt).toLocaleString() : ''}} | Updated: ${{q.updatedAt ? new Date(q.updatedAt).toLocaleString() : ''}}
                            </div>
                        </div>`
                    ).join('');
                    document.getElementById('questions').innerHTML = questionsHtml;
                }}
            }} catch (error) {{
                console.error('Error loading questions:', error);
            }}
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
