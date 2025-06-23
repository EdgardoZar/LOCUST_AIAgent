"""
This script serves as the entry point for running LLM analysis from the Jenkins pipeline.
"""
import os
import argparse
import csv
import json
import re
from llm_analyzer import LLMAnalyzer

def find_latest_reports(reports_dir):
    """Finds the most recent stats and HTML report files based on available _stats.csv files."""
    if not os.path.isdir(reports_dir):
        raise FileNotFoundError(f"Reports directory not found: {reports_dir}")

    # 1. Find all stats files, which are essential for the analysis
    stats_files = [f for f in os.listdir(reports_dir) if f.endswith('_stats.csv')]
    if not stats_files:
        raise FileNotFoundError("No _stats.csv files found in the reports directory.")

    # 2. Extract timestamps from the stats files and find the latest one
    timestamp_pattern = re.compile(r'(\d{8}_\d{6})')
    
    latest_timestamp = ''
    latest_stats_file = ''

    for f in stats_files:
        match = timestamp_pattern.search(f)
        if match:
            timestamp = match.group(1)
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_stats_file = f
    
    if not latest_stats_file:
        raise ValueError("Could not determine the latest stats file from available files.")

    print(f"Found latest stats file: {latest_stats_file}")
    stats_file_path = os.path.join(reports_dir, latest_stats_file)

    # 3. Now, find the corresponding HTML file for that same timestamp (it's optional)
    html_file_path = None
    # The HTML file will have the timestamp preceded by an underscore and followed by a dot
    html_file_candidate_name_part = f"_{latest_timestamp}.html"
    for f in os.listdir(reports_dir):
        if f.endswith(html_file_candidate_name_part):
             # To be extra sure, check that the main name part also matches
             stats_prefix = latest_stats_file.split(f'_{latest_timestamp}_')[0]
             html_prefix = f.split(f'_{latest_timestamp}.')[0]
             if stats_prefix == html_prefix:
                html_file_path = os.path.join(reports_dir, f)
                break

    return stats_file_path, html_file_path

def read_summary_stats(stats_file_path):
    """Reads the aggregated summary row from the _stats.csv file."""
    with open(stats_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        # The last row is the aggregated summary
        for row in reader:
            pass
        # This is now the last row
        summary_row = row
    
    # Assuming standard Locust CSV format
    return {
        "total_requests": int(summary_row[2]),
        "failed_requests": int(summary_row[3]),
        "requests_per_sec": float(summary_row[5]),
        "avg_response_time": float(summary_row[7]),
    }

def format_as_markdown(analysis_data, scenario_name, test_run_id):
    """Formats the LLM analysis JSON into a Markdown report."""
    
    grade_emojis = {
        "EXCELLENT": "✅",
        "GOOD": "👍",
        "ACCEPTABLE": "👌",
        "POOR": "👎",
        "FAILED": "❌",
        "UNKNOWN": "❓"
    }

    markdown = f"# 📊 LLM Performance Analysis Report\n\n"
    markdown += f"## Test Scenario: `{scenario_name}`\n"
    markdown += f"**Test Run ID:** `{test_run_id}`\n\n"
    
    grade = analysis_data.get('performance_grade', 'UNKNOWN')
    markdown += f"## 📈 Performance Grade: {grade} {grade_emojis.get(grade, '')}\n\n"

    markdown += f"### 📝 Summary\n"
    markdown += f"{analysis_data.get('summary', 'No summary provided.')}\n\n"

    markdown += "### 💡 Key Insights\n"
    for insight in analysis_data.get('key_insights', []):
        markdown += f"- {insight}\n"
    markdown += "\n"
    
    markdown += "### 🛠️ Recommendations\n"
    for rec in analysis_data.get('recommendations', []):
        markdown += f"- {rec}\n"
    markdown += "\n"
    
    markdown += "### 🚨 Potential Issues & Concerns\n"
    for issue in analysis_data.get('issues', []):
        markdown += f"- {issue}\n"
    markdown += "\n"

    markdown += f"### 💼 Business Impact\n"
    markdown += f"{analysis_data.get('business_impact', 'Not assessed.')}\n\n"
    
    markdown += "### 🚀 Next Steps\n"
    for step in analysis_data.get('next_steps', []):
        markdown += f"- {step}\n"
    
    return markdown

def main():
    parser = argparse.ArgumentParser(description="Run LLM analysis on Locust test results.")
    parser.add_argument("--reports_dir", required=True, help="Directory containing Locust report files.")
    parser.add_argument("--analysis_dir", required=True, help="Directory to save the analysis markdown file.")
    parser.add_argument("--scenario_name", required=True, help="Name of the test scenario.")
    parser.add_argument("--test_run_id", required=True, help="Unique ID for the test run.")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="The OpenAI model to use for analysis.")
    args = parser.parse_args()

    # API Key is expected to be in the environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return

    try:
        print(f"Searching for reports in: {args.reports_dir}")
        stats_csv_path, html_report_path = find_latest_reports(args.reports_dir)

        if not stats_csv_path:
            print("ERROR: Could not find the latest _stats.csv file.")
            return

        print(f"Found stats file: {stats_csv_path}")
        print(f"Found HTML report: {html_report_path}")

        # Prepare context for the analyzer
        summary_stats = read_summary_stats(stats_csv_path)
        test_results_context = {
            "scenario_name": args.scenario_name,
            "success": True, # Assuming the test itself ran successfully
            **summary_stats
        }

        # Run analysis
        print(f"Using AI model: {args.model}")
        analyzer = LLMAnalyzer(api_key=api_key, model=args.model)
        analysis_json = analyzer.analyze_test_results(test_results_context, html_report_path)
        
        print("\nLLM Analysis (JSON):\n", json.dumps(analysis_json, indent=2))

        # Format as markdown
        markdown_report = format_as_markdown(analysis_json, args.scenario_name, args.test_run_id)

        # Save markdown file
        os.makedirs(args.analysis_dir, exist_ok=True)
        report_filename = f"{args.scenario_name.replace(' ', '_')}_{args.test_run_id}_analysis.md"
        report_path = os.path.join(args.analysis_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(markdown_report)
        
        print(f"\n✅ Successfully generated analysis report: {report_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 