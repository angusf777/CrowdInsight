#!/usr/bin/env python3
"""
Canceled Projects Distribution Visualization

This module generates a visualization showing the distribution of canceled Kickstarter 
projects based on the percentage of time remaining at cancellation. It helps visualize
the preprocessing methodology used to handle canceled projects in the CrowdInsight pipeline.

The visualization includes:
- Histogram of canceled projects by percentage of time remaining at cancellation
- Visual indicator of the 60% threshold used to convert some canceled projects to failed status
- Summary statistics showing total canceled projects and their handling

Usage:
    python plot_canceled_distribution.py

Output:
    Creates and saves 'Graphs/canceled_projects_distribution.png'

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

def plot_canceled_projects_distribution():
    """
    Generate a graph showing the distribution of canceled Kickstarter projects 
    by percentage of time remaining at cancellation.
    
    The function:
    1. Loads canceled project statistics from filtering_stats.json
    2. Creates a histogram of projects by time remaining at cancellation
    3. Adds a threshold line showing the 60% cutoff used for conversion to failed status
    4. Includes annotations explaining the preprocessing methodology
    5. Displays summary statistics on the graph
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
    
    # Prepare for plotting
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create the bar chart
    bars = ax.bar(percentages, counts, width=0.5, alpha=0.7, color='skyblue', edgecolor='navy')
    
    # Add a vertical line at 60% (the conversion threshold)
    threshold = 60
    ax.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
               label=f'Conversion Threshold ({threshold}%)')
    
    # Add text annotations for the areas
    ax.text(threshold/2, max(counts) * 0.9, "Converted to Failed",
            ha='center', fontsize=12, bbox=dict(facecolor='lightblue', alpha=0.5))
    ax.text((100+threshold)/2, max(counts) * 0.9, "Excluded from Dataset",
            ha='center', fontsize=12, bbox=dict(facecolor='lightsalmon', alpha=0.5))
    
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
    
    # Add labels and title
    ax.set_xlabel('Percentage of Time Remaining at Cancellation', fontsize=12)
    ax.set_ylabel('Number of Projects', fontsize=12)
    ax.set_title('Distribution of Canceled Kickstarter Projects by Time Remaining', fontsize=14)
    
    # Set x-axis limits
    ax.set_xlim(-2, 102)
    
    # Add gridlines for readability
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add legend
    ax.legend()
    
    # Save the figure
    os.makedirs('Graphs', exist_ok=True)
    output_file = os.path.join('Graphs', 'canceled_projects_distribution.png')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Graph saved to {output_file}")
    
    # Close the figure to free memory
    plt.close()

if __name__ == "__main__":
    plot_canceled_projects_distribution() 