"""
This script serves as the entry point for running LLM analysis from the Jenkins pipeline.
"""
import os
import argparse
import csv
import json
from llm_analyzer import LLMAnalyzer

def find_latest_reports(reports_dir):
    """Finds the most recent stats and HTML report files based on timestamp."""
    if not os.path.isdir(reports_dir):
        raise FileNotFoundError(f"Reports directory not found: {reports_dir}")

    files = [f for f in os.listdir(reports_dir) if '_stats.csv' in f or f.endswith('.html')]
    if not files:
        return None, None

    # Extract timestamps and sort
    timestamps = sorted(list(set([f.split('_')[-2] + '_' + f.split('_')[-1].split('.')[0] for f in files])), reverse=True)
    latest_timestamp = timestamps[0]

    stats_file = next((os.path.join(reports_dir, f) for f in files if latest_timestamp in f and f.endswith('_stats.csv')), None)
    html_file = next((os.path.join(reports_dir, f) for f in files if latest_timestamp in f and f.endswith('.html')), None)

    return stats_file, html_file

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