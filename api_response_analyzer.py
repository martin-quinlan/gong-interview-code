# API Response Analyser for Integration Troubleshooting
# 
# This script analyses API responses for a customer over a specified date range
# to identify patterns in failed requests. It helps support engineers diagnose
# integration issues by revealing common errors, response time problems, and
# time-based patterns in API failures.

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def fetch_api_logs(customer_id, start_date, end_date):
    """
    Fetch API logs from database for the specified customer and date range.
    This would typically connect to your logging database.
    
    Parameters:
        customer_id (str): Unique identifier for the customer
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
        
    Returns:
        list: Collection of API log entries
    """
    # This is a placeholder - in production, this would query your logging system
    # Example implementation might use SQL:
    #
    # conn = database.connect(connection_string)
    # query = """
    #     SELECT request_id, timestamp, endpoint, status_code, 
    #            response_time_ms, error_message
    #     FROM api_logs
    #     WHERE customer_id = %s AND timestamp BETWEEN %s AND %s
    # """
    # results = conn.execute(query, [customer_id, start_date, end_date])
    # return results.fetchall()
    
    # For demonstration, return mock data
    return [
        {
            'request_id': f'req-{i}',
            'timestamp': datetime.strptime(start_date, '%Y-%m-%d') + timedelta(hours=i % 24),
            'endpoint': f'/api/{"calls" if i % 3 == 0 else "users" if i % 3 == 1 else "integrations"}',
            'status_code': 200 if i % 5 != 0 else 400 + (i % 3) * 10,
            'response_time_ms': 150 + (i * 10) % 500,
            'error_message': None if i % 5 != 0 else f'Error type {i % 3}'
        }
        for i in range(100)
    ]


def analyse_api_responses(customer_id, start_date, end_date):
    """
    Analyse API responses for a customer over a specified date range
    to identify patterns in failed requests.
    
    Parameters:
        customer_id (str): Unique identifier for the customer
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
        
    Returns:
        dict: Analysis report with various metrics and error patterns
    """
    # Fetch API logs from database
    logs = fetch_api_logs(customer_id, start_date, end_date)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(logs)
    
    # Analyse response codes
    response_summary = df.groupby('status_code').agg({
        'request_id': 'count',
        'response_time_ms': ['mean', 'median', 'max']
    }).reset_index()
    
    # Identify slow endpoints
    endpoint_performance = df.groupby('endpoint').agg({
        'request_id': 'count',
        'response_time_ms': ['mean', 'median', 'max'],
        'status_code': lambda x: (x < 400).mean() * 100  # Success rate percentage
    }).reset_index()
    
    # Analyse error patterns
    error_df = df[df['status_code'] >= 400]
    error_patterns = {}
    
    if not error_df.empty:
        error_patterns = error_df.groupby(['endpoint', 'error_message']).size().reset_index(name='count')
        error_patterns = error_patterns.sort_values('count', ascending=False)
    
    # Time-based pattern analysis
    df['hour_of_day'] = df['timestamp'].dt.hour
    hourly_errors = df[df['status_code'] >= 400].groupby('hour_of_day').size()
    
    # Look for correlation between response time and errors
    time_vs_errors = {}
    if not error_df.empty:
        time_thresholds = [100, 250, 500, 1000, float('inf')]
        for i in range(len(time_thresholds)-1):
            lower = time_thresholds[i]
            upper = time_thresholds[i+1]
            time_range = f"{lower}-{upper if upper != float('inf') else '+'}"
            count_in_range = len(df[(df['response_time_ms'] > lower) & 
                                   (df['response_time_ms'] <= upper)])
            errors_in_range = len(df[(df['response_time_ms'] > lower) & 
                                    (df['response_time_ms'] <= upper) & 
                                    (df['status_code'] >= 400)])
            
            if count_in_range > 0:
                error_rate = errors_in_range / count_in_range * 100
            else:
                error_rate = 0
                
            time_vs_errors[time_range] = {
                'total_requests': count_in_range,
                'error_count': errors_in_range,
                'error_rate': error_rate
            }
    
    # Generate comprehensive report
    report = {
        'analysis_period': {
            'start_date': start_date,
            'end_date': end_date,
            'customer_id': customer_id
        },
        'overall_metrics': {
            'total_requests': len(df),
            'success_rate': (df['status_code'] < 400).mean() * 100,
            'average_response_time': df['response_time_ms'].mean(),
            'error_count': len(df[df['status_code'] >= 400])
        },
        'response_code_summary': response_summary.to_dict(),
        'endpoint_performance': endpoint_performance.to_dict(),
        'top_errors': error_patterns.to_dict() if isinstance(error_patterns, pd.DataFrame) else {},
        'hourly_error_distribution': hourly_errors.to_dict(),
        'response_time_vs_errors': time_vs_errors
    }
    
    # Generate recommendations based on findings
    recommendations = []
    
    # High error rates for specific endpoints
    if isinstance(endpoint_performance, pd.DataFrame) and not endpoint_performance.empty:
        problem_endpoints = endpoint_performance[endpoint_performance['status_code'] < 95]
        for _, row in problem_endpoints.iterrows():
            recommendations.append(f"Investigate high error rate ({100-row['status_code']:.1f}%) for endpoint: {row['endpoint']}")
    
    # Slow endpoints
    if isinstance(endpoint_performance, pd.DataFrame) and not endpoint_performance.empty:
        slow_endpoints = endpoint_performance[endpoint_performance[('response_time_ms', 'mean')] > 300]
        for _, row in slow_endpoints.iterrows():
            recommendations.append(f"Optimise performance for slow endpoint: {row['endpoint']} (avg: {row[('response_time_ms', 'mean')]:.0f}ms)")
    
    # Time-based issues
    if len(hourly_errors) > 0:
        peak_hour = hourly_errors.idxmax()
        peak_count = hourly_errors.max()
        if peak_count > len(df) * 0.1:  # If peak hour has >10% of all errors
            recommendations.append(f"Investigate potential issues during peak error hour: {peak_hour}:00")
    
    report['recommendations'] = recommendations
    
    return report


if __name__ == "__main__":
    # Example usage
    customer_id = "CUST12345"
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    
    analysis = analyse_api_responses(customer_id, start_date, end_date)
    
    # Print summary results
    print(f"Analysis for customer {customer_id} from {start_date} to {end_date}")
    print(f"Total requests: {analysis['overall_metrics']['total_requests']}")
    print(f"Success rate: {analysis['overall_metrics']['success_rate']:.2f}%")
    print(f"Average response time: {analysis['overall_metrics']['average_response_time']:.2f}ms")
    print(f"Error count: {analysis['overall_metrics']['error_count']}")
    
    # Print recommendations
    print("\nRecommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {rec}")
