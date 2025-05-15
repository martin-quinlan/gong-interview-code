# Log Analyser for Error Pattern Detection
#
# This script analyses log files to identify error patterns within a specified time window.
# It's designed to help support engineers quickly identify common errors, their frequency,
# and any time-based patterns that might indicate systemic issues.
#
# Features:
# - Filters logs by time window to focus on recent issues
# - Normalises error messages to group similar errors
# - Analyses error distribution by hour to identify patterns
# - Generates comprehensive reports for further analysis

import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

def analyse_log_file(log_file_path, time_window=24):
    """
    Analyse a log file to identify error patterns within a specific time window
    
    Args:
        log_file_path (str): Path to the log file
        time_window (int): Hours to look back from now
    
    Returns:
        dict: Analysis report containing error statistics and patterns
    """
    if not os.path.exists(log_file_path):
        return {"error": f"Log file not found: {log_file_path}"}
    
    # Define regex patterns for log parsing
    timestamp_pattern = r'\[(.*?)\]'
    level_pattern = r'\[(INFO|WARNING|ERROR|CRITICAL)\]'
    error_pattern = r'ERROR.*?:\s(.*?)(?:\n|$)'
    
    # Initialise data structures
    log_entries = []
    
    # Calculate time threshold
    time_threshold = datetime.now() - timedelta(hours=time_window)
    
    # Process log file
    print(f"Analysing log file: {log_file_path}")
    print(f"Looking at entries from the past {time_window} hours")
    
    try:
        with open(log_file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                # Extract timestamp
                timestamp_match = re.search(timestamp_pattern, line)
                if timestamp_match:
                    try:
                        # Try different timestamp formats - adjust as needed for your logs
                        timestamp_formats = [
                            '%Y-%m-%d %H:%M:%S,%f',
                            '%Y-%m-%d %H:%M:%S.%f',
                            '%Y-%m-%d %H:%M:%S',
                            '%d/%b/%Y:%H:%M:%S'
                        ]
                        
                        timestamp_str = timestamp_match.group(1)
                        timestamp = None
                        
                        for fmt in timestamp_formats:
                            try:
                                timestamp = datetime.strptime(timestamp_str, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if timestamp is None:
                            # If all formats failed, skip this line
                            continue
                        
                        # Skip if outside time window
                        if timestamp < time_threshold:
                            continue
                            
                        # Extract log level
                        level_match = re.search(level_pattern, line)
                        level = level_match.group(1) if level_match else 'UNKNOWN'
                        
                        # Extract error message for ERROR logs
                        error_msg = None
                        if level == 'ERROR' or level == 'CRITICAL':
                            error_match = re.search(error_pattern, line)
                            if error_match:
                                error_msg = error_match.group(1)
                            elif 'ERROR' in line or 'CRITICAL' in line:
                                # If regex failed but it's an error, get everything after the level marker
                                parts = line.split(f"[{level}]", 1)
                                if len(parts) > 1:
                                    error_msg = parts[1].strip()
                        
                        # Add to our data
                        log_entries.append({
                            'timestamp': timestamp,
                            'level': level,
                            'error_msg': error_msg,
                            'raw_log': line.strip(),
                            'line_number': line_number
                        })
                    except Exception as e:
                        print(f"Error parsing line {line_number}: {e}")
                        continue
    except Exception as e:
        return {"error": f"Failed to process log file: {str(e)}"}
    
    # If no entries were found, return early
    if not log_entries:
        return {
            "warning": "No log entries found within the specified time window",
            "total_logs": 0,
            "error_logs": 0
        }
    
    # Convert to DataFrame for analysis
    log_df = pd.DataFrame(log_entries)
    
    # Basic statistics
    total_logs = len(log_df)
    error_count = len(log_df[(log_df['level'] == 'ERROR') | (log_df['level'] == 'CRITICAL')])
    
    # Error type frequency analysis
    error_types = Counter()
    normalised_to_original = {}  # To keep track of normalising
    
    for error in log_df[(log_df['level'] == 'ERROR') | (log_df['level'] == 'CRITICAL')]['error_msg'].dropna():
        # Normalise error message to group similar errors
        # 1. Replace UUIDs with <UUID>
        normalised_error = re.sub(r'[0-9a-f-]{36}', '<UUID>', error)
        # 2. Replace numbers with <NUM>
        normalised_error = re.sub(r'\b\d+\b', '<NUM>', normalised_error)
        # 3. Replace file paths with <PATH>
        normalised_error = re.sub(r'\/[\w\/\.-]+', '<PATH>', normalised_error)
        # 4. Replace IP addresses with <IP>
        normalised_error = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '<IP>', normalised_error)
        # 5. Replace email addresses with <EMAIL>
        normalised_error = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', normalised_error)
        
        error_types[normalised_error] += 1
        normalised_to_original[normalised_error] = error  # Store original example
    
    # Error time distribution
    log_df['hour'] = log_df['timestamp'].dt.hour
    hourly_errors = log_df[(log_df['level'] == 'ERROR') | (log_df['level'] == 'CRITICAL')].groupby('hour').size()
    
    # Log level distribution
    level_counts = log_df['level'].value_counts().to_dict()
    
    # Identify error bursts (multiple errors in short time periods)
    error_df = log_df[(log_df['level'] == 'ERROR') | (log_df['level'] == 'CRITICAL')]
    error_bursts = []
    
    if not error_df.empty:
        # Sort by timestamp
        error_df = error_df.sort_values('timestamp')
        
        # Define what constitutes a "burst" (e.g., 5+ errors within 5 minutes)
        burst_threshold = 5
        time_threshold_minutes = 5
        
        # Initialise variables
        current_burst = []
        
        # Iterate through errors to find bursts
        for i in range(len(error_df)):
            if i == 0:
                current_burst = [i]
                continue
                
            current_time = error_df.iloc[i]['timestamp']
            previous_time = error_df.iloc[current_burst[-1]]['timestamp']
            
            # If this error is within the time threshold of the previous one, add to current burst
            if (current_time - previous_time).total_seconds() / 60 <= time_threshold_minutes:
                current_burst.append(i)
            else:
                # If we had a burst, record it
                if len(current_burst) >= burst_threshold:
                    start_time = error_df.iloc[current_burst[0]]['timestamp']
                    end_time = error_df.iloc[current_burst[-1]]['timestamp']
                    error_bursts.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration_minutes': (end_time - start_time).total_seconds() / 60,
                        'error_count': len(current_burst),
                        'sample_errors': error_df.iloc[current_burst[:3]]['error_msg'].tolist()
                    })
                # Start a new burst
                current_burst = [i]
        
        # Check if the last group is a burst
        if len(current_burst) >= burst_threshold:
            start_time = error_df.iloc[current_burst[0]]['timestamp']
            end_time = error_df.iloc[current_burst[-1]]['timestamp']
            error_bursts.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': (end_time - start_time).total_seconds() / 60,
                'error_count': len(current_burst),
                'sample_errors': error_df.iloc[current_burst[:3]]['error_msg'].tolist()
            })
    
    # Generate comprehensive report
    report = {
        'total_logs': total_logs,
        'error_logs': error_count,
        'error_percentage': (error_count / total_logs) * 100 if total_logs > 0 else 0,
        'top_error_types': [
            {
                'pattern': error,
                'count': count,
                'percentage': (count / error_count) * 100 if error_count > 0 else 0,
                'example': normalised_to_original.get(error, 'No example available')
            }
            for error, count in error_types.most_common(10)
        ],
        'hourly_error_distribution': hourly_errors.to_dict(),
        'level_distribution': level_counts,
        'error_bursts': error_bursts
    }
    
    # Generate recommendations based on analysis
    recommendations = []
    
    # High frequency errors
    if error_count > 0:
        top_errors = error_types.most_common(3)
        for error, count in top_errors:
            if count > 5:  # Threshold for "significant" errors
                percentage = (count / error_count) * 100
                recommendations.append(f"Investigate frequent error pattern ({percentage:.1f}% of errors): {error[:100]}...")
    
    # Error bursts
    if error_bursts:
        recommendations.append(f"Examine {len(error_bursts)} error bursts that may indicate systemic issues")
        for i, burst in enumerate(error_bursts[:3], 1):  # Show details for top 3 bursts
            recommendations.append(f"  Burst {i}: {burst['error_count']} errors in {burst['duration_minutes']:.1f} minutes at {burst['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Time-based patterns
    if not hourly_errors.empty:
        peak_hour = hourly_errors.idxmax()
        peak_count = hourly_errors.max()
        if peak_count > error_count * 0.3:  # If >30% of errors occur in one hour
            recommendations.append(f"Check for scheduled jobs at hour {peak_hour}:00 that may be causing {peak_count} errors ({(peak_count/error_count)*100:.1f}% of total)")
    
    report['recommendations'] = recommendations
    
    return report

def plot_error_distribution(report, output_path=None):
    """
    Generate visualisations of error patterns from the analysis report
    
    Args:
        report (dict): Analysis report from analyse_log_file
        output_path (str, optional): Path to save the visualisation. If None, displays plot instead
    """
    if 'error' in report or report.get('total_logs', 0) == 0:
        print("No data to visualise")
        return
    
    # Create figure with subplots
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Error distribution by hour
    hours = list(report['hourly_error_distribution'].keys())
    counts = list(report['hourly_error_distribution'].values())
    
    sorted_hours = sorted(hours)
    sorted_counts = [report['hourly_error_distribution'][h] for h in sorted_hours]
    
    axs[0].bar(sorted_hours, sorted_counts, color='#1f77b4')
    axs[0].set_title('Error Distribution by Hour')
    axs[0].set_xlabel('Hour of Day')
    axs[0].set_ylabel('Number of Errors')
    axs[0].set_xticks(range(0, 24, 2))
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot 2: Top error types
    labels = [f"{e['pattern'][:40]}..." for e in report['top_error_types'][:5]]
    sizes = [e['count'] for e in report['top_error_types'][:5]]
    
    if labels and sizes:
        axs[1].pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
        axs[1].set_title('Top 5 Error Types')
        # Add legend
        axs[1].legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))
    else:
        axs[1].text(0.5, 0.5, 'No error data available', ha='center', va='center')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Visualisation saved to {output_path}")
    else:
        plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyse log files for error patterns')
    parser.add_argument('log_file', help='Path to the log file')
    parser.add_argument('--time-window', type=int, default=24, help='Hours to look back from now (default: 24)')
    parser.add_argument('--visualise', action='store_true', help='Generate visualisation of error patterns')
    parser.add_argument('--output', help='Path to save visualisation (if --visualise is used)')
    
    args = parser.parse_args()
    
    report = analyse_log_file(args.log_file, args.time_window)
    
    if 'error' in report:
        print(f"Error: {report['error']}")
    else:
        print(f"\nLog Analysis Results:")
        print(f"Total logs analysed: {report['total_logs']}")
        print(f"Error logs found: {report['error_logs']} ({report['error_percentage']:.2f}%)")
        
        print("\nTop Error Patterns:")
        for i, error in enumerate(report['top_error_types'][:5], 1):
            print(f"{i}. [{error['count']} occurrences] {error['pattern'][:100]}")
            print(f"   Example: {error['example'][:100]}")
        
        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        if args.visualise:
            plot_error_distribution(report, args.output)
