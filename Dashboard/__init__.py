import azure.functions as func
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Dashboard function processed a request.')
        host = req.headers.get('host', 'your-function-app.azurewebsites.net')
        base_url = f"https://{host}/api"
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Police Chatbot Analytics Dashboard</title>
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
            <h1>🚔 Police Chatbot Analytics Dashboard</h1>
            <p>Real-time insights into citizen interactions</p>
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
                    <div class="metric-value" id="satisfaction">0</div>
                    <div class="metric-label">Avg Satisfaction</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="resolutionRate">0%</div>
                    <div class="metric-label">Resolution Rate</div>
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
            document.getElementById('satisfaction').textContent = data.summary?.avgSatisfactionScore || 0;
            document.getElementById('resolutionRate').textContent = data.summary?.resolutionRate || '0%';
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
                    `<div class="question-item">
                        <div class="question-text">${{q.question || 'No question recorded'}}</div>
                        <div class="question-meta">
                            Category: ${{q.category}} |
                            Satisfaction: ${{q.satisfaction || 'N/A'}} |
                            ${{new Date(q.timestamp).toLocaleString()}}
                        </div>
                    </div>`
                ).join('');
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
            }};
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
            }};
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
        """.format(base_url=base_url)
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
