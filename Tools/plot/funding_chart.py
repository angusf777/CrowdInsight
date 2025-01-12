"""
Create bar charts for Kickstarter funding goal distribution analysis.

This module creates visualizations for funding goal distributions,
using alternating grey shades and clean, minimal styling.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

def plot_funding_distribution(distribution: Dict[str, int]):
    """
    Create a bar chart of funding goal distribution with alternating grey colors.
    
    Args:
        distribution: Dictionary mapping funding ranges to project counts
    """
    # Create figure with specific dimensions (382x276 pixels)
    dpi = 100
    width_inches = 382 / dpi
    height_inches = 276 / dpi
    
    # Set up the plot style
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial']
    
    # Create figure with light grey background
    fig = plt.figure(figsize=(width_inches, height_inches), facecolor='#F9F9F9')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#F9F9F9')
    
    # Prepare data
    ranges = list(distribution.keys())
    # Format ranges for vertical alignment
    formatted_ranges = [range_label.replace('-', '\n') for range_label in ranges]
    counts = list(distribution.values())
    x_pos = np.arange(len(ranges))
    
    # Define alternating grey colors
    colors = ['#4D4D4D', '#808080']  # Dark grey and medium grey
    bar_colors = [colors[i % 2] for i in range(len(ranges))]
    
    # Create bars with equal width
    width = 0.8  # Fixed width for all bars
    bars = ax.bar(x_pos, counts, width=width, color=bar_colors)
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f'{int(height):,}',
                ha='center', va='bottom',
                fontsize=11,
                fontweight='bold',
                family='Arial')
    
    # Customize the plot
    ax.set_xticks(x_pos)
    ax.set_xticklabels(formatted_ranges, fontsize=9, family='Arial')
    
    # Remove all spines and axis
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.set_visible(False)
    
    # Remove grid
    ax.grid(False)
    
    # Adjust layout with more space for vertical labels
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2, left=0.02, right=0.98, top=0.9)
    
    return fig

def save_plot(fig, output_path: str = "Graphs/funding_distribution.png"):
    """Save the plot to a file."""
    # Ensure the Graphs directory exists
    output_dir = Path("Graphs")
    output_dir.mkdir(exist_ok=True)
    
    # Save with specific dimensions and proper background color
    fig.savefig(output_path, dpi=100, bbox_inches='tight', pad_inches=0.1,
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)  # Close the figure to free memory

def create_funding_chart(distribution: Dict[str, int]):
    """
    Create and save a funding distribution bar chart.
    
    Args:
        distribution: Dictionary mapping funding ranges to project counts
    """
    fig = plot_funding_distribution(distribution)
    save_plot(fig) 