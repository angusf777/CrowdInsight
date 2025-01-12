"""Create visualizations for backer funding analysis."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Optional

def clean_category_label(label: str, category: Optional[str] = None) -> str:
    """Clean up category labels by removing the category prefix if present."""
    if category and label.lower().startswith(f"{category.lower()}/"):
        return label[len(category) + 1:]  # +1 for the '/'
    return label

def create_backer_funding_chart(categories: List[str], averages: List[float], category: Optional[str] = None):
    """Create a minimalist line chart showing average funding per backer."""
    # Calculate dimensions in inches (952x250 pixels at 100 DPI)
    width_inches = 9.52  # 952/100
    height_inches = 2.50  # 250/100
    
    # Create figure with specified dimensions
    fig = plt.figure(figsize=(width_inches, height_inches), facecolor='#F9F9F9')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#F9F9F9')
    
    # Clean up category labels
    clean_categories = [clean_category_label(cat, category) for cat in categories]
    
    # Plot data with improved styling
    x = np.arange(len(categories))
    line = ax.plot(x, averages, color='#FF7F50', marker='o', linewidth=3, markersize=10,
                  markerfacecolor='white', markeredgecolor='#FF7F50', markeredgewidth=2)[0]
    
    # Add subtle gridlines
    ax.grid(True, axis='y', linestyle='--', alpha=0.2, color='gray')
    
    # Add value labels above points with improved spacing
    for i, avg in enumerate(averages):
        ax.annotate(
            f'${avg:,.0f}',
            xy=(i, avg),
            xytext=(0, 15),  # Increased spacing
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=10,
            fontfamily='Arial',
            weight='bold'
        )
    
    # Customize appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    ax.tick_params(axis='y', which='both', length=0)
    ax.set_xticks(x)
    ax.set_xticklabels(clean_categories, rotation=45, ha='right', fontsize=10, fontfamily='Arial')
    
    # Remove y-axis ticks and labels
    ax.set_yticks([])
    
    # Add padding to prevent label cutoff
    plt.subplots_adjust(bottom=0.25, left=0.02, right=0.98, top=0.85)
    
    # Save the plot
    output_dir = Path('Graphs')
    output_dir.mkdir(exist_ok=True)
    plt.savefig(
        output_dir / 'backer_funding_distribution.png',
        dpi=100,
        bbox_inches='tight',
        pad_inches=0.1,  # Added padding
        facecolor='#F9F9F9',
        edgecolor='none'
    )
    plt.close() 