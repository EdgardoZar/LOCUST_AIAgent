"""
This script serves as the entry point for running LLM analysis from the Jenkins pipeline.
"""
import os
import argparse
import csv
import json
import re
from llm_analyzer import LLMAnalyzer

def clean_emoji_characters(text):
    """Remove emoji characters from text to ensure Windows compatibility."""
    # Remove emoji characters using Unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_json_content(data):
    """Recursively clean emoji characters from JSON content."""
    if isinstance(data, dict):
        return {key: clean_json_content(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json_content(item) for item in data]
    elif isinstance(data, str):
        return clean_emoji_characters(data)
    else:
        return data

def find_latest_reports(reports_dir):
    """Finds the most recent stats and HTML report files based on available _stats.csv files."""
    if not os.path.isdir(reports_dir):
        raise FileNotFoundError(f"Reports directory not found: {reports_dir}")

    print(f"Searching for reports in: {reports_dir}")
    
    # 1. Find all stats files recursively, which are essential for the analysis
    stats_files = []
    for root, dirs, files in os.walk(reports_dir):
        for file in files:
            if file.endswith('_stats.csv'):
                stats_files.append(os.path.join(root, file))
    
    print(f"Found {len(stats_files)} stats files:")
    for stats_file in stats_files:
        print(f"  - {stats_file}")
    
    if not stats_files:
        raise FileNotFoundError("No _stats.csv files found in the reports directory.")

    # 2. Extract timestamps from the stats files and find the latest one
    timestamp_pattern = re.compile(r'(\d{8}_\d{6})')
    
    latest_timestamp = ''
    latest_stats_file = ''

    for stats_file_path in stats_files:
        # Try to extract timestamp from the directory name first (more reliable)
        dir_name = os.path.basename(os.path.dirname(stats_file_path))
        match = timestamp_pattern.search(dir_name)
        
        if not match:
            # Fallback: try to extract from filename
            match = timestamp_pattern.search(os.path.basename(stats_file_path))
        
        if match:
            timestamp = match.group(1)
            print(f"  Found timestamp {timestamp} in {stats_file_path}")
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_stats_file = stats_file_path
    
    if not latest_stats_file:
        raise ValueError("Could not determine the latest stats file from available files.")

    print(f"Selected latest stats file: {latest_stats_file}")
    stats_file_path = latest_stats_file

    # 3. Now, find the corresponding HTML file in the same directory
    html_file_path = None
    stats_dir = os.path.dirname(stats_file_path)
    
    print(f"Looking for HTML file in directory: {stats_dir}")
    
    # Look for HTML file in the same directory as the stats file
    for file in os.listdir(stats_dir):
        if file.endswith('.html'):
            html_file_path = os.path.join(stats_dir, file)
            print(f"Found HTML file: {html_file_path}")
            break
    
    if not html_file_path:
        print("No HTML file found in the same directory as stats file")

    return stats_file_path, html_file_path

def read_summary_stats(stats_file_path):
    """Reads the aggregated summary row from the _stats.csv file."""
    try:
        with open(stats_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            # Read all rows and filter out any that are empty
            all_rows = [row for row in reader if row]

        if not all_rows:
            raise ValueError(f"The stats file is empty or contains only blank lines: {stats_file_path}")

        # The last non-empty row should be the aggregated summary
        summary_row = all_rows[-1]

        # A valid summary row should have at least 16 columns for percentiles
        if len(summary_row) < 16:
            raise ValueError(f"The summary row in {stats_file_path} is missing percentile data. Content: {summary_row}")

        # Assuming standard Locust CSV format
        return {
            "total_requests": int(summary_row[2]),
            "failed_requests": int(summary_row[3]),
            "requests_per_sec": float(summary_row[5]),
            "avg_response_time": float(summary_row[7]),
            "p90_response_time": float(summary_row[14]),
            "p95_response_time": float(summary_row[15]),
        }
    except (ValueError, IndexError) as e:
        print(f"Error processing stats file {stats_file_path}: {e}")
        # Re-raise the exception to ensure the pipeline fails clearly
        raise

def format_as_markdown(analysis_data, scenario_name, test_run_id):
    """Formats the LLM analysis JSON into a Markdown report."""
    
    # Use text alternatives instead of emojis for better Windows compatibility
    grade_indicators = {
        "EXCELLENT": "[EXCELLENT]",
        "GOOD": "[GOOD]",
        "ACCEPTABLE": "[ACCEPTABLE]",
        "POOR": "[POOR]",
        "FAILED": "[FAILED]",
        "UNKNOWN": "[UNKNOWN]"
    }

    markdown = f"# LLM Performance Analysis Report\n\n"
    markdown += f"## Test Scenario: `{scenario_name}`\n"
    markdown += f"**Test Run ID:** `{test_run_id}`\n\n"
    
    grade = analysis_data.get('performance_grade', 'UNKNOWN')
    markdown += f"## Performance Grade: {grade} {grade_indicators.get(grade, '')}\n\n"

    markdown += f"### Summary\n"
    markdown += f"{analysis_data.get('summary', 'No summary provided.')}\n\n"

    # Add the new response time table
    markdown += "### Response Time Analysis\n"
    table_data = analysis_data.get('response_time_table', [])
    if table_data:
        markdown += "| Metric | Value |\n"
        markdown += "|---|---|\n"
        for row in table_data:
            markdown += f"| {row.get('Metric')} | {row.get('Value')} |\n"
        markdown += "\n"

    markdown += "### Key Insights\n"
    for insight in analysis_data.get('key_insights', []):
        markdown += f"- {insight}\n"
    markdown += "\n"
    
    markdown += "### Recommendations\n"
    for rec in analysis_data.get('recommendations', []):
        markdown += f"- {rec}\n"
    markdown += "\n"
    
    markdown += "### Potential Issues & Concerns\n"
    for issue in analysis_data.get('issues', []):
        markdown += f"- {issue}\n"
    markdown += "\n"

    markdown += f"### Business Impact\n"
    markdown += f"{analysis_data.get('business_impact', 'Not assessed.')}\n\n"
    
    markdown += "### Next Steps\n"
    for step in analysis_data.get('next_steps', []):
        markdown += f"- {step}\n"
    
    return markdown

def main():
    parser = argparse.ArgumentParser(description="Run LLM analysis on Locust test results.")
    parser.add_argument("--reports_dir", required=True, help="Directory containing Locust report files.")
    parser.add_argument("--analysis_dir", required=True, help="Directory to save the analysis markdown file.")
    parser.add_argument("--scenario_name", required=True, help="Name of the test scenario.")
    parser.add_argument("--test_run_id", required=True, help="Unique ID for the test run.")
    parser.add_argument("--users", required=True, help="Number of concurrent users for the test.")
    parser.add_argument("--run_time", required=True, help="Duration of the test.")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="The OpenAI model to use for analysis.")
    args = parser.parse_args()

    # API Key is expected to be in the environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return

    try:
        print(f"Searching for reports in: {args.reports_dir}")
        
        # Check if reports directory exists
        if not os.path.exists(args.reports_dir):
            print(f"ERROR: Reports directory does not exist: {args.reports_dir}")
            print("Available directories:")
            workspace_dir = os.path.dirname(args.reports_dir)
            if os.path.exists(workspace_dir):
                for item in os.listdir(workspace_dir):
                    item_path = os.path.join(workspace_dir, item)
                    if os.path.isdir(item_path):
                        print(f"  - {item}")
            return
        
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
            "users": args.users,
            "run_time": args.run_time,
            **summary_stats
        }

        # Run analysis
        print(f"Using AI model: {args.model}")
        analyzer = LLMAnalyzer(api_key=api_key, model=args.model)
        analysis_json = analyzer.analyze_test_results(test_results_context, html_report_path)
        
        print("\nLLM Analysis (JSON):\n", json.dumps(analysis_json, indent=2))

        # Clean emoji characters from the analysis JSON
        cleaned_analysis_json = clean_json_content(analysis_json)
        
        # Debug: Check if there are still emoji characters
        analysis_json_str = json.dumps(cleaned_analysis_json, indent=2)
        if '\u2705' in analysis_json_str:
            print("WARNING: Found \\u2705 character in cleaned JSON, removing it...")
            analysis_json_str = analysis_json_str.replace('\u2705', '[SUCCESS]')
            cleaned_analysis_json = json.loads(analysis_json_str)

        # Format as markdown
        markdown_report = format_as_markdown(cleaned_analysis_json, args.scenario_name, args.test_run_id)
        
        # Final check: Clean any remaining emoji characters from markdown
        markdown_report = clean_emoji_characters(markdown_report)

        # Save markdown file
        os.makedirs(args.analysis_dir, exist_ok=True)
        report_filename = f"{args.scenario_name.replace(' ', '_')}_{args.test_run_id}_analysis.md"
        report_path = os.path.join(args.analysis_dir, report_filename)
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(markdown_report)
            print(f"\n[SUCCESS] Successfully generated analysis report: {report_path}")
        except UnicodeEncodeError as e:
            print(f"Warning: Unicode encoding error when writing file: {e}")
            print("Attempting to write file with ASCII encoding...")
            try:
                # Fallback: write with ASCII encoding, replacing problematic characters
                with open(report_path, "w", encoding="ascii", errors="replace") as f:
                    f.write(markdown_report)
                print(f"[SUCCESS] Successfully generated analysis report (ASCII): {report_path}")
            except Exception as e2:
                print(f"Error: Could not write file even with ASCII encoding: {e2}")
                raise
        except Exception as e:
            print(f"Error writing markdown file: {e}")
            raise

    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        print("This usually means the test execution did not generate the expected report files.")
        print("Please check that:")
        print("1. The test execution completed successfully")
        print("2. CSV reports were generated")
        print("3. The reports directory structure is correct")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 