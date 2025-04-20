"""
Kickstarter Category Growth Visualization

This module creates line plots visualizing the growth trends of Kickstarter 
categories or subcategories. It generates clean, minimalist charts that 
highlight relative growth rates with annotations showing exact percentage changes.

The visualizations are designed to be embedded in web dashboards or reports
and provide insights into which categories are trending upward or downward
in terms of project counts or funding amounts.

Features:
- Minimalist design with clean typography
- Clear growth rate indicators with value annotations
- Adjustable dimensions to fit various display contexts
- Automatic file handling and directory creation

Usage:
    This module is typically imported and used by analysis scripts
    rather than run directly:
    
    from Tools.plot import trending_cat
    trending_cat.create_growth_plot(categories_data, sort_by="projects")

Copyright (c) 2025 Angus Fung
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

def plot_category_growth(categories: List[str], growth_rates: List[float], title: str = "") -> plt.Figure:
    """
    Create a line plot of category growth rates with point labels.
    
    This function generates a minimalist line visualization showing growth rates
    for categories, with each data point annotated with the exact percentage value.
    The design emphasizes readability and clean aesthetics for dashboard integration.
    
    Args:
        categories: List of category names to display
        growth_rates: List of growth rate percentages corresponding to categories
        title: Optional plot title (default empty)
        
    Returns:
        plt.Figure: Matplotlib figure object containing the visualization
        
    Note:
        The function uses a fixed size ratio optimized for dashboard embedding,
        with specific styling choices for readability.
    """
    # Create figure and axis with specific dimensions (280x952 pixels)
    dpi = 100
    width_inches = 952 / dpi
    height_inches = 280 / dpi
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial']  # Use Arial as primary sans-serif font
    
    # Create figure with white background
    fig = plt.figure(figsize=(width_inches, height_inches), facecolor='#F9F9F9')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#F9F9F9')
    
    # Create x positions
    x_pos = np.arange(len(categories))
    
    # Plot line and points
    ax.plot(x_pos, growth_rates, 'b-', alpha=0.3)  # Line with low alpha
    ax.scatter(x_pos, growth_rates, color='blue', s=50)  # Smaller points
    
    # Add value labels on points
    for i, (growth, cat) in enumerate(zip(growth_rates, categories)):
        label = f"{growth:+.1f}%" if growth != 0 else "0%"
        y_offset = 5 if growth >= 0 else -15  # Adjust label position based on value
        ax.annotate(label,
                   (i, growth),
                   textcoords="offset points",
                   xytext=(0, y_offset),
                   ha='center',
                   fontsize=12,
                   fontweight='bold')
    
    # Capitalize first letter of each category
    categories = [cat.capitalize() for cat in categories]
    
    # Customize the plot
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=0, ha='center', fontsize=12)
    ax.spines['left'].set_visible(False)   # Remove left spine
    ax.spines['top'].set_visible(False)    # Remove top spine
    ax.spines['right'].set_visible(False)  # Remove right spine
    ax.spines['bottom'].set_visible(False) # Remove x-axis line
    ax.yaxis.set_visible(False)  # Hide y-axis ticks and labels
    ax.grid(False)  # Remove grid
    
    # Remove scale by setting y-axis limits based on data
    max_growth = max(growth_rates)
    min_growth = min(growth_rates)
    padding = (max_growth - min_growth) * 0.2  # 20% padding
    ax.set_ylim(min_growth - padding, max_growth + padding)
    
    # Adjust layout with more bottom margin to prevent label trimming
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2, left=0.02, right=0.98, top=0.98)  # Increased bottom margin for larger font
    
    return fig

def save_plot(fig: plt.Figure, output_path: str = "Graphs/category_growth.png") -> None:
    """
    Save the plot to a file with appropriate settings.
    
    This function handles directory creation and saves the figure with
    settings optimized for web display, preserving transparency and
    background colors.
    
    Args:
        fig: Matplotlib figure object to save
        output_path: Path where the figure should be saved (default: Graphs/category_growth.png)
        
    Note:
        Creates the output directory if it doesn't exist
    """
    # Ensure the Graphs directory exists
    output_dir = Path("Graphs")
    output_dir.mkdir(exist_ok=True)
    
    # Save with specific dimensions (280x952 pixels) and proper background color
    fig.savefig(output_path, dpi=100, bbox_inches='tight', pad_inches=0.1, 
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)  # Close the figure to free memory

def create_growth_plot(sorted_categories: List[Tuple[str, Dict[str, Any]]], sort_by: str = 'projects') -> None:
    """
    Create and save a growth rate plot from category metrics.
    
    This function extracts growth rate data from category metrics and
    generates a visualization highlighting the growth trends. It's designed 
    to be called from analysis scripts that have already calculated metrics
    and growth rates.
    
    Args:
        sorted_categories: List of tuples containing (category_name, metrics_dict)
                          where metrics_dict must contain a 'growth' key
        sort_by: Metric used for sorting, either 'projects' or 'funds'
                (affects display only, not the sorting of the input data)
    
    Note:
        The function automatically selects the top 5 categories from the input list
    """
    # Extract categories and growth rates
    categories = []
    growth_rates = []
    
    for cat_name, metrics in sorted_categories[:5]:  # Take top 5
        categories.append(cat_name)
        sort_key = 'total_funds' if sort_by == 'funds' else 'total_projects'
        growth_rates.append(metrics['growth'])
    
    # Create and save the plot
    fig = plot_category_growth(categories, growth_rates)
    save_plot(fig) 