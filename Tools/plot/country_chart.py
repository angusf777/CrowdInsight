"""
Kickstarter Country Distribution Visualization

This module creates bar charts visualizing the distribution of Kickstarter projects 
across different countries. It generates clean, professional visualizations that
help identify geographic patterns in crowdfunding activity.

The visualizations use alternating grey tones for bars and are designed with
careful typography and spacing to maximize readability in reports and dashboards.
Long country names are automatically formatted to display properly.

Features:
- Alternating grey shades for adjacent bars
- Automatic formatting of long country names
- Value labels on top of each bar
- Clean, minimalist design without axes or grids
- Consistent sizing for dashboard integration

Usage:
    This module is typically imported and used by analysis scripts
    rather than run directly:
    
    from Tools.plot import country_chart
    country_chart.create_country_chart(country_distribution_data)

Copyright (c) 2025 Angus Fung
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict

def format_country_name(name: str) -> str:
    """
    Format country name by splitting into two lines if too long.
    
    This function ensures long country names are displayed properly in
    the bar chart by splitting them across multiple lines if needed.
    
    Args:
        name: Country name to format
        
    Returns:
        str: Formatted country name, possibly with newlines inserted
        
    Examples:
        >>> format_country_name("United States")
        'United\\nStates'
        >>> format_country_name("France")
        'France'
    """
    if len(name) <= 10:
        return name
        
    # Handle multi-word names
    words = name.split()
    if len(words) > 1:
        mid = len(words) // 2
        return '\n'.join([' '.join(words[:mid]), ' '.join(words[mid:])])
    
    # Handle single long words
    mid = len(name) // 2
    return name[:mid] + '\n' + name[mid:]

def plot_country_distribution(distribution: Dict[str, int]) -> plt.Figure:
    """
    Create a bar chart showing the distribution of projects across countries.
    
    This function generates a professional bar chart visualization with
    alternating grey tones, value labels on each bar, and careful typography.
    Country names are automatically formatted for readability.
    
    Args:
        distribution: Dictionary mapping country names to project counts
        
    Returns:
        plt.Figure: Matplotlib figure object containing the visualization
        
    Note:
        The function uses a fixed size ratio (382x276 pixels) optimized for
        dashboard embedding, with specific styling choices for readability.
    """
    # Convert pixels to inches (DPI = 100)
    width_inches = 382 / 100
    height_inches = 276 / 100
    
    # Create figure with specified dimensions and background color
    fig = plt.figure(figsize=(width_inches, height_inches), facecolor='#F9F9F9')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#F9F9F9')
    
    # Prepare data
    countries = [format_country_name(country) for country in distribution.keys()]
    values = list(distribution.values())
    x = np.arange(len(countries))
    
    # Define colors (alternating greys)
    colors = ['#404040', '#595959', '#737373', '#8C8C8C', '#A6A6A6', '#BFBFBF']
    
    # Create bars
    bars = ax.bar(x, values, width=0.8, color=colors)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=10, fontfamily='Arial')
    
    # Customize plot
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=8, fontfamily='Arial')
    
    # Remove axes and spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_yticks([])
    
    # Adjust layout for two-line labels
    plt.subplots_adjust(bottom=0.25, left=0.02, right=0.98, top=0.98)
    
    return fig

def save_plot(fig: plt.Figure, output_path: str = "Graphs/country_distribution.png") -> None:
    """
    Save the plot to the specified path with optimized settings.
    
    This function handles directory creation and saves the figure with
    settings optimized for web display, preserving transparency and
    background colors.
    
    Args:
        fig: Matplotlib figure object to save
        output_path: Path where the figure should be saved (default: Graphs/country_distribution.png)
        
    Note:
        Creates the output directory if it doesn't exist
    """
    output_dir = Path(output_path).parent
    output_dir.mkdir(exist_ok=True)
    
    fig.savefig(output_path, dpi=100, bbox_inches='tight', pad_inches=0,
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

def create_country_chart(distribution: Dict[str, int]) -> None:
    """
    Create and save a bar chart of country distribution.
    
    This function serves as the main entry point for generating country
    distribution visualizations. It takes a dictionary of country counts,
    creates a bar chart, and saves it to the default location.
    
    Args:
        distribution: Dictionary mapping country names to project counts
        
    Example:
        >>> country_data = {"United States": 1500, "United Kingdom": 800, "Canada": 400}
        >>> create_country_chart(country_data)
    """
    fig = plot_country_distribution(distribution)
    save_plot(fig) 