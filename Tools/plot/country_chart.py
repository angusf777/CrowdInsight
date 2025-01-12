"""Create bar charts for Kickstarter country distribution analysis."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict

def format_country_name(name: str) -> str:
    """Format country name by splitting into two lines if too long."""
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
    """Create a bar chart showing the distribution of projects across countries."""
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

def save_plot(fig: plt.Figure, output_path: str = "Graphs/country_distribution.png"):
    """Save the plot to the specified path."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(exist_ok=True)
    
    fig.savefig(output_path, dpi=100, bbox_inches='tight', pad_inches=0,
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

def create_country_chart(distribution: Dict[str, int]):
    """Create and save a bar chart of country distribution."""
    fig = plot_country_distribution(distribution)
    save_plot(fig) 