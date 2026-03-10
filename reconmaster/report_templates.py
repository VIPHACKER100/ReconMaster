from datetime import datetime
import json
import re

def generate_premium_html_report(recon, duration: str, end_dt: datetime) -> str:
    """Generate high-fidelity premium HTML report with interactive visualizations"""
    
    # Prepare data for charts
    severity_counts = {
        "critical": len([v for v in recon.vulns if v.get("info", {}).get("severity") == "critical"]),
        "high": len([v for v in recon.vulns if v.get("info", {}).get("severity") == "high"]),
        "medium": len([v for v in recon.vulns if v.get("info", {}).get("severity") == "medium"]),
        "low": len([v for v in recon.vulns if v.get("info", {}).get("severity") == "low"]),
        "info": len([v for v in recon.vulns if v.get("info", {}).get("severity") == "info"]),
    }

    # Calculate technology distribution
    tech_dist = {}
    for techs in recon.tech_stack.values():
        if techs:
            for t in techs:
                t_str = str(t)
                tech_dist[t_str] = tech_dist.get(t_str, 0) + 1
    top_techs = dict(sorted(tech_dist.items(), key=lambda x: x[1], reverse=True)[:10])

    def _calculate_risk_score() -> int:
        score = 0
        severity_map = {"critical": 30, "high": 15, "medium": 5, "low": 1}
        for v in recon.vulns:
            sev = v.get("info", {}).get("severity", "info").lower()
            score += severity_map.get(sev, 0)
        return min(score, 100)

    def _generate_ai_profile(vuln: dict) -> str:
        info = vuln.get('info', {}) or {}
        severity = info.get('severity', 'info')
        plugin = vuln.get('plugin', 'Core')
        
        profiles = {
            "critical": "This finding represents an immediate risk of system compromise. Automated analysis suggests a high likelihood of exploitability.",
            "high": "A severe security bypass or data exposure has been identified. Immediate remediation is recommended.",
            "medium": "A potential security weakness has been identified. It provides significant leverage for an attacker.",
            "low": "This finding indicates a deviation from security best practices.",
            "info": "Security discovery providing additional context on the attack surface."
        }
        return f"[{plugin}] {profiles.get(severity.lower(), profiles['info'])}"

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titan Dashboard 2.0 - {recon.target}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0f172a;
            --sidebar: #1e293b;
            --card: rgba(30, 41, 59, 0.7);
            --accent: #38bdf8;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --critical: #ef4444;
            --high: #f97316;
            --medium: #eab308;
            --low: #22c55e;
            --info: #3b82f6;
        }}
        * {{ box-sizing: border-box; transition: all 0.2s ease-in-out; scroll-behavior: smooth; }}
        body {{ font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text-main); margin: 0; display: flex; min-height: 100vh; }}
        sidebar {{ width: 280px; background: var(--sidebar); border-right: 1px solid #1f2937; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; position: sticky; top: 0; height: 100vh; }}
        .logo {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); letter-spacing: -1px; }}
        nav {{ display: flex; flex-direction: column; gap: 0.5rem; }}
        nav a {{ padding: 0.75rem 1rem; border-radius: 8px; color: var(--text-dim); text-decoration: none; font-weight: 500; }}
        nav a:hover, nav a.active {{ background: #0f172a; color: var(--accent); }}
        main {{ flex: 1; padding: 3rem; overflow-y: auto; max-width: 1200px; margin: 0 auto; }}
        .header {{ margin-bottom: 3rem; }}
        .header h1 {{ font-size: 2.5rem; margin: 0; font-weight: 700; background: linear-gradient(90deg, #fff, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .stat-card {{ background: var(--card); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); text-align: left; position: relative; }}
        .stat-card .label {{ color: var(--text-dim); font-size: 0.875rem; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2rem; font-weight: 700; margin-top: 0.5rem; color: var(--accent); }}
        .chart-container {{ background: var(--card); padding: 2rem; border-radius: 20px; margin-bottom: 3rem; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
        .chart-box {{ height: 350px; }}
        section {{ margin-bottom: 4rem; }}
        .finding-item {{ background: var(--card); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid #334155; }}
        .severity-pill {{ padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .bg-critical {{ background: rgba(239, 68, 68, 0.15); color: var(--critical); }}
        .tech-tag {{ display: inline-block; background: #1e293b; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; margin-right: 6px; color: var(--accent); }}
    </style>
</head>
<body>
    <sidebar>
        <div class="logo">Titan v4.2.0</div>
        <nav>
            <a href="#overview" class="active">Overview</a>
            <a href="#vulnerabilities">Findings</a>
            <a href="#technologies">Tech Stack</a>
        </nav>
    </sidebar>
    <main>
        <div class="header">
            <h1>{recon.target}</h1>
            <p>Assessment Duration: {duration} | Date: {end_dt.strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Risk Score</div>
                <div class="value">{_calculate_risk_score()}/100</div>
            </div>
            <div class="stat-card">
                <div class="label">Vulnerabilities</div>
                <div class="value">{len(recon.vulns)}</div>
            </div>
        </div>
        <div class="chart-container">
            <div class="chart-box"><canvas id="severityChart"></canvas></div>
            <div class="chart-box"><canvas id="techChart"></canvas></div>
        </div>
        <section id="vulnerabilities">
            <h2>Findings</h2>
            {"".join([f'''
            <div class="finding-item">
                <span class="severity-pill bg-{v.get('info', {}).get('severity', 'info').lower()}">{v.get('info', {}).get('severity', 'info')}</span>
                <strong>{v.get('info', {}).get('name', 'Finding')}</strong>
                <p>{v.get('matched-at', 'N/A')}</p>
                <div style="font-size: 0.85rem; color: var(--text-dim);">{_generate_ai_profile(v)}</div>
            </div>
            ''' for v in recon.vulns]) if recon.vulns else "<p>No findings.</p>"}
        </section>
    </main>
    <script>
        const sevCtx = document.getElementById('severityChart').getContext('2d');
        new Chart(sevCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
                datasets: [{{
                    data: [{severity_counts['critical']}, {severity_counts['high']}, {severity_counts['medium']}, {severity_counts['low']}, {severity_counts['info']}],
                    backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'],
                    borderWidth: 0
                }}]
            }},
            options: {{ maintainAspectRatio: false }}
        }});
        const techCtx = document.getElementById('techChart').getContext('2d');
        new Chart(techCtx, {{
            type: 'bar',
            data: {{
                labels: {list(top_techs.keys())},
                datasets: [{{
                    label: 'Count',
                    data: {list(top_techs.values())},
                    backgroundColor: '#38bdf8'
                }}]
            }},
            options: {{ indexAxis: 'y', maintainAspectRatio: false }}
        }});
    </script>
</body>
</html>
"""
    return html_template
