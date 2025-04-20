#!/usr/bin/env python3
"""
Advanced Canceled Projects Distribution Visualization

This module generates detailed visualizations showing the distribution of canceled 
Kickstarter projects based on the percentage of time remaining at cancellation. 
It offers more comprehensive insights than the basic visualization by providing
both a histogram and cumulative distribution function (CDF).

The visualization includes:
- Top panel: Histogram of canceled projects by percentage of time remaining
- Bottom panel: Cumulative distribution function (CDF) showing percentage of projects
  below each threshold
- Annotation showing the exact percentage of projects below the 60% conversion threshold
- Comprehensive statistical summary

Usage:
    python plot_canceled_distribution_advanced.py

Output:
    Creates and saves 'Graphs/canceled_projects_advanced.png'

The script requires 'Data/filtering_stats.json' to be present, which is generated
by running the 'filter_kickstarter.py' script as part of the data processing pipeline.

Copyright (c) 2025 Angus Fung
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from matplotlib.gridspec import GridSpec

def plot_canceled_projects_advanced():
    """
    Generate advanced visualizations of canceled Kickstarter projects distribution
    by percentage of time remaining at cancellation, including both histogram and CDF.
    
    The function:
    1. Loads canceled project statistics from filtering_stats.json
    2. Creates a multi-panel figure with two visualizations:
       - Histogram showing the raw distribution of projects
       - Cumulative distribution function showing the percentage of projects
         below each time-remaining threshold
    3. Adds annotations explaining the preprocessing methodology
    4. Highlights the 60% threshold used for conversion to failed status
    5. Displays comprehensive summary statistics
    6. Saves the visualization to the Graphs directory
    
    Returns:
        None: The function saves a PNG file but does not return any values
        
    Raises:
        FileNotFoundError: If the required statistics file is not found
    """
    # Define the stats file path
    stats_file = Path("Data/filtering_stats.json")
    
    # Check if the file exists
    if not stats_file.exists():
        print(f"Error: {stats_file} not found. Run filter_kickstarter.py first.")
        return
    
    # Load the filtering statistics
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    # Extract the time remaining percentages and counts
    if "canceled" not in stats or "by_time_remaining" not in stats["canceled"]:
        print("Error: Canceled projects statistics not found in the file.")
        return
    
    time_remaining_data = stats["canceled"]["by_time_remaining"]
    
    # Convert to sorted lists for plotting
    percentages = []
    counts = []
    
    # Sort by percentage value (as float)
    for percentage_str, count in sorted(time_remaining_data.items(), key=lambda x: float(x[0].strip('%'))):
        percentages.append(float(percentage_str.strip('%')))
        counts.append(count)
    
    # Calculate cumulative counts for CDF
    cumulative_counts = np.cumsum(counts)
    total_projects = sum(counts)
    cumulative_percentage = 100 * cumulative_counts / total_projects
    
    # Prepare for plotting
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(2, 1, height_ratios=[2, 1], hspace=0.3)
    
    # First subplot: Histogram
    ax1 = fig.add_subplot(gs[0])
    
    # Create the bar chart
    bars = ax1.bar(percentages, counts, width=0.5, alpha=0.7, color='skyblue', edgecolor='navy')
    
    # Add a vertical line at 60% (the conversion threshold)
    threshold = 60
    ax1.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
                label=f'Conversion Threshold ({threshold}%)')
    
    # Add text annotations for the areas
    ax1.text(threshold/2, max(counts) * 0.9, "Converted to Failed",
             ha='center', fontsize=10, bbox=dict(facecolor='lightblue', alpha=0.5))
    ax1.text((100+threshold)/2, max(counts) * 0.9, "Excluded from Dataset",
             ha='center', fontsize=10, bbox=dict(facecolor='lightsalmon', alpha=0.5))
    
    # Add labels and title for first subplot
    ax1.set_xlabel('Percentage of Time Remaining at Cancellation', fontsize=12)
    ax1.set_ylabel('Number of Projects', fontsize=12)
    ax1.set_title('Distribution of Canceled Kickstarter Projects by Time Remaining', fontsize=14)
    
    # Set x-axis limits
    ax1.set_xlim(-2, 102)
    
    # Add gridlines for readability
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.legend()
    
    # Second subplot: Cumulative Distribution Function (CDF)
    ax2 = fig.add_subplot(gs[1])
    
    # Plot the CDF
    ax2.plot(percentages, cumulative_percentage, 'o-', color='green', linewidth=2, 
            label='Cumulative Distribution')
    
    # Add the threshold line
    ax2.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
               label=f'Conversion Threshold ({threshold}%)')
    
    # Find the y-value at the threshold for annotation
    threshold_idx = percentages.index(next((p for p in percentages if p >= threshold), percentages[-1]))
    threshold_y = cumulative_percentage[threshold_idx-1] if threshold_idx > 0 else 0
    
    # Add an annotation at the threshold point
    ax2.annotate(f'{threshold_y:.1f}% of cancellations', 
                xy=(threshold, threshold_y), 
                xytext=(threshold+5, threshold_y-5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                fontsize=10)
    
    # Add labels for second subplot
    ax2.set_xlabel('Percentage of Time Remaining at Cancellation', fontsize=12)
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12)
    ax2.set_title('Cumulative Distribution of Canceled Projects', fontsize=14)
    
    # Set limits
    ax2.set_xlim(-2, 102)
    ax2.set_ylim(0, 102)
    
    # Add gridlines
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Add summary statistics as text
    total_canceled = stats["canceled"]["total"]
    converted = stats["canceled"]["converted_to_failed"]
    excluded = stats["canceled"]["excluded_early"]
    
    summary_text = (
        f"Total canceled projects: {total_canceled}\n"
        f"Converted to failed: {converted} ({converted/total_canceled:.1%})\n"
        f"Excluded (>60% remaining): {excluded} ({excluded/total_canceled:.1%})"
    )
    
    plt.figtext(0.15, 0.02, summary_text, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
    
    # Save the figure
    os.makedirs('Graphs', exist_ok=True)
    output_file = os.path.join('Graphs', 'canceled_projects_advanced.png')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Advanced graph saved to {output_file}")
    
    # Close the figure to free memory
    plt.close()

if __name__ == "__main__":
    plot_canceled_projects_advanced() 