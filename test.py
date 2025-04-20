#!/usr/bin/env python3
import json
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.ticker as ticker

def analyze_field_lengths(data, field_name, count_type="characters"):
    """
    Calculate statistics for the lengths of a specified field in the data.
    
    Parameters:
    data -- The JSON data
    field_name -- The field to analyze
    count_type -- 'characters' or 'words' to determine the counting method
    """
    # Extract lengths of the specified field
    lengths = []
    for key, item in data.items():
        if field_name in item and item[field_name]:
            if count_type == "characters":
                lengths.append(len(item[field_name]))
            elif count_type == "words":
                # Count words by splitting on whitespace
                words = item[field_name].split()
                lengths.append(len(words))
    
    if not lengths:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "lengths": []
        }
    
    # Calculate statistics
    return {
        "min": min(lengths),
        "max": max(lengths),
        "mean": np.mean(lengths),
        "median": np.median(lengths),
        "lengths": lengths
    }

def analyze_numerical_field(data, field_name, condition_field=None, condition_value=None):
    """Analyze numerical field values with optional condition filtering."""
    values = []
    
    for key, item in data.items():
        # Check if the field exists and has a value
        if field_name in item and item[field_name] is not None:
            # If condition is specified, check if it's met
            if condition_field is not None and condition_value is not None:
                if condition_field in item and item[condition_field] == condition_value:
                    values.append(item[field_name])
            else:
                values.append(item[field_name])
    
    if not values:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "values": []
        }
    
    # Calculate statistics
    return {
        "min": min(values),
        "max": max(values),
        "mean": np.mean(values),
        "median": np.median(values),
        "values": values
    }

def plot_distribution(lengths, title, filename, unit="characters"):
    """Create a PDF graph of the distribution of lengths."""
    plt.figure(figsize=(10, 6))
    
    # Filter to only the middle 95% of data
    lower_limit = np.percentile(lengths, 2.5)
    upper_limit = np.percentile(lengths, 97.5)
    filtered_lengths = [l for l in lengths if lower_limit <= l <= upper_limit]
    
    # Create a histogram
    n, bins, patches = plt.hist(filtered_lengths, bins=50, density=True, alpha=0.6, color='skyblue', label='Histogram')
    
    # Add a kernel density estimate (KDE) to show the PDF
    try:
        kde = stats.gaussian_kde(filtered_lengths)
        x = np.linspace(min(filtered_lengths), max(filtered_lengths), 1000)
        plt.plot(x, kde(x), 'r-', linewidth=2, label='PDF')
    except np.linalg.LinAlgError:
        # If KDE fails (e.g., singular matrix), just skip the line
        print(f"Warning: Could not generate KDE for {filename}")
    
    # Format x-axis with thousands separators for readability
    plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Add labels and title
    plt.xlabel(f'Length ({unit})')
    plt.ylabel('Density')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add note about data filtering
    if len(filtered_lengths) < len(lengths):
        plt.figtext(0.5, 0.01, f"Note: Only showing middle 95% of data ({len(filtered_lengths)} of {len(lengths)} points)",
                   ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
    
    # Save the figure
    plt.tight_layout()
    os.makedirs('Graphs', exist_ok=True)
    plt.savefig(os.path.join('Graphs', filename))
    print(f"Graph saved to Graphs/{filename}")
    
    # Close the figure to free memory
    plt.close()

def plot_numerical_distribution(values, title, filename, x_label):
    """Create a PDF graph of the distribution of numerical values."""
    plt.figure(figsize=(10, 6))
    
    # Filter to only the middle 95% of data
    lower_limit = np.percentile(values, 2.5)
    upper_limit = np.percentile(values, 97.5)
    filtered_values = [v for v in values if lower_limit <= v <= upper_limit]
    
    # Create a histogram
    n, bins, patches = plt.hist(filtered_values, bins=50, density=True, alpha=0.6, color='skyblue', label='Histogram')
    
    # Add a kernel density estimate (KDE) to show the PDF
    try:
        kde = stats.gaussian_kde(filtered_values)
        x = np.linspace(min(filtered_values), max(filtered_values), 1000)
        plt.plot(x, kde(x), 'r-', linewidth=2, label='PDF')
    except np.linalg.LinAlgError:
        # If KDE fails (e.g., singular matrix), just skip the line
        print(f"Warning: Could not generate KDE for {filename}")
    
    # Format x-axis with thousands separators for readability
    plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel('Density')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add note about data filtering
    if len(filtered_values) < len(values):
        plt.figtext(0.5, 0.01, f"Note: Only showing middle 95% of data ({len(filtered_values)} of {len(values)} points)",
                   ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
    
    # Save the figure
    plt.tight_layout()
    os.makedirs('Graphs', exist_ok=True)
    plt.savefig(os.path.join('Graphs', filename))
    print(f"Graph saved to Graphs/{filename}")
    
    # Close the figure to free memory
    plt.close()

def plot_comparison(desc_lengths, risk_lengths, title, filename, unit="characters"):
    """Create a combined plot comparing both distributions using linear scale."""
    plt.figure(figsize=(12, 7))
    
    # Filter to only the middle 95% of data
    desc_lower = np.percentile(desc_lengths, 2.5)
    desc_upper = np.percentile(desc_lengths, 97.5)
    risk_lower = np.percentile(risk_lengths, 2.5)
    risk_upper = np.percentile(risk_lengths, 97.5)
    
    filtered_desc = [l for l in desc_lengths if desc_lower <= l <= desc_upper]
    filtered_risk = [l for l in risk_lengths if risk_lower <= l <= risk_upper]
    
    # Create KDE plots for both distributions
    kde_desc = stats.gaussian_kde(filtered_desc)
    kde_risk = stats.gaussian_kde(filtered_risk)
    
    # Use linear scale for x-axis for better visualization
    x_desc = np.linspace(min(filtered_desc), max(filtered_desc), 1000)
    x_risk = np.linspace(min(filtered_risk), max(filtered_risk), 1000)
    
    plt.plot(x_desc, kde_desc(x_desc), 'b-', linewidth=2, label=f'Description ({unit})')
    plt.plot(x_risk, kde_risk(x_risk), 'r-', linewidth=2, label=f'Risk ({unit})')
    
    # Format x-axis with thousands separators for readability
    plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Add labels and title
    plt.xlabel(f'Length ({unit})')
    plt.ylabel('Density')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add note about data filtering
    plt.figtext(0.5, 0.01, 
               f"Note: Only showing middle 95% of data (Description: {len(filtered_desc)} of {len(desc_lengths)}, Risk: {len(filtered_risk)} of {len(risk_lengths)})",
               ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
    
    # Save the figure
    plt.tight_layout()
    os.makedirs('Graphs', exist_ok=True)
    plt.savefig(os.path.join('Graphs', filename))
    print(f"Graph saved to Graphs/{filename}")
    
    # Close the figure to free memory
    plt.close()

def main():
    """Main function to analyze the JSON file."""
    # Define the path to the JSON file
    json_file = os.path.join("Data", "pre_inputdata.json")
    
    # Check if the file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
        return
    
    try:
        # Load the JSON data
        print(f"Loading data from {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Analyzing data from {len(data)} records...")
        
        # Analyze character lengths
        print("\n=== CHARACTER COUNT ANALYSIS ===")
        description_char_stats = analyze_field_lengths(data, "description", "characters")
        risks_char_stats = analyze_field_lengths(data, "risk", "characters")
        
        # Print character count results
        print("\nDescription Character Length Statistics:")
        if description_char_stats["min"] is not None:
            print(f"Min: {description_char_stats['min']}")
            print(f"Max: {description_char_stats['max']}")
            print(f"Mean: {description_char_stats['mean']:.2f}")
            print(f"Median: {description_char_stats['median']:.2f}")
        else:
            print("No description fields found in the data.")
        
        print("\nRisks Character Length Statistics:")
        if risks_char_stats["min"] is not None:
            print(f"Min: {risks_char_stats['min']}")
            print(f"Max: {risks_char_stats['max']}")
            print(f"Mean: {risks_char_stats['mean']:.2f}")
            print(f"Median: {risks_char_stats['median']:.2f}")
        else:
            print("No risk fields found in the data.")
        
        # Analyze word counts
        print("\n=== WORD COUNT ANALYSIS ===")
        description_word_stats = analyze_field_lengths(data, "description", "words")
        risks_word_stats = analyze_field_lengths(data, "risk", "words")
        
        # Print word count results
        print("\nDescription Word Count Statistics:")
        if description_word_stats["min"] is not None:
            print(f"Min: {description_word_stats['min']}")
            print(f"Max: {description_word_stats['max']}")
            print(f"Mean: {description_word_stats['mean']:.2f}")
            print(f"Median: {description_word_stats['median']:.2f}")
        else:
            print("No description fields found in the data.")
        
        print("\nRisks Word Count Statistics:")
        if risks_word_stats["min"] is not None:
            print(f"Min: {risks_word_stats['min']}")
            print(f"Max: {risks_word_stats['max']}")
            print(f"Mean: {risks_word_stats['mean']:.2f}")
            print(f"Median: {risks_word_stats['median']:.2f}")
        else:
            print("No risk fields found in the data.")
        
        # Analyze funding goal distribution
        funding_goal_stats = analyze_numerical_field(data, "funding_goal")
        
        # Analyze average funding goal of previous projects (only for projects with previous projects)
        avg_funding_prev_stats = analyze_numerical_field(data, "average_funding_goal", "previous_projects", 1)
        
        # Analyze pledged amount of previous projects (only for projects with previous projects)
        pledged_prev_stats = analyze_numerical_field(data, "average_pledged", "previous_projects", 1)
        
        # Print funding goal statistics
        print("\nFunding Goal Statistics:")
        if funding_goal_stats["min"] is not None:
            print(f"Min: ${funding_goal_stats['min']:.2f}")
            print(f"Max: ${funding_goal_stats['max']:.2f}")
            print(f"Mean: ${funding_goal_stats['mean']:.2f}")
            print(f"Median: ${funding_goal_stats['median']:.2f}")
        else:
            print("No funding goal data found.")
        
        # Print average funding goal of previous projects statistics
        print("\nAverage Funding Goal of Previous Projects Statistics (only for projects with previous projects):")
        if avg_funding_prev_stats["min"] is not None:
            print(f"Min: ${avg_funding_prev_stats['min']:.2f}")
            print(f"Max: ${avg_funding_prev_stats['max']:.2f}")
            print(f"Mean: ${avg_funding_prev_stats['mean']:.2f}")
            print(f"Median: ${avg_funding_prev_stats['median']:.2f}")
            print(f"Count: {len(avg_funding_prev_stats['values'])}")
        else:
            print("No data found for projects with previous funding goals.")
        
        # Print pledged amount of previous projects statistics
        print("\nPledged Amount of Previous Projects Statistics (only for projects with previous projects):")
        if pledged_prev_stats["min"] is not None:
            print(f"Min: ${pledged_prev_stats['min']:.2f}")
            print(f"Max: ${pledged_prev_stats['max']:.2f}")
            print(f"Mean: ${pledged_prev_stats['mean']:.2f}")
            print(f"Median: ${pledged_prev_stats['median']:.2f}")
            print(f"Count: {len(pledged_prev_stats['values'])}")
        else:
            print("No data found for projects with previous pledged amounts.")
        
        # Generate PDF graphs if data is available
        print("\nGenerating PDF graphs...")
        
        # Character length distributions
        if description_char_stats["lengths"]:
            plot_distribution(description_char_stats["lengths"], 
                             "Distribution of Description Lengths (Characters)", 
                             "description_char_length_pdf.png",
                             "characters")
            
        if risks_char_stats["lengths"]:
            plot_distribution(risks_char_stats["lengths"], 
                             "Distribution of Risk Lengths (Characters)", 
                             "risk_char_length_pdf.png",
                             "characters")
            
        # Generate comparison graph for character lengths
        if description_char_stats["lengths"] and risks_char_stats["lengths"]:
            plot_comparison(description_char_stats["lengths"], risks_char_stats["lengths"],
                           "Comparison of Description and Risk Length Distributions (Characters)",
                           "comparison_char_pdf.png",
                           "characters")
        
        # Word count distributions
        if description_word_stats["lengths"]:
            plot_distribution(description_word_stats["lengths"], 
                             "Distribution of Description Lengths (Words)", 
                             "description_word_count_pdf.png",
                             "words")
            
        if risks_word_stats["lengths"]:
            plot_distribution(risks_word_stats["lengths"], 
                             "Distribution of Risk Lengths (Words)", 
                             "risk_word_count_pdf.png",
                             "words")
            
        # Generate comparison graph for word counts
        if description_word_stats["lengths"] and risks_word_stats["lengths"]:
            plot_comparison(description_word_stats["lengths"], risks_word_stats["lengths"],
                           "Comparison of Description and Risk Length Distributions (Words)",
                           "comparison_word_pdf.png",
                           "words")
            
        # Funding goal distribution
        if funding_goal_stats["values"]:
            plot_numerical_distribution(funding_goal_stats["values"],
                                       "Distribution of Funding Goals",
                                       "funding_goal_distribution.png",
                                       "Funding Goal ($)")
            
        # Average funding goal of previous projects distribution
        if avg_funding_prev_stats["values"]:
            plot_numerical_distribution(avg_funding_prev_stats["values"],
                                       "Distribution of Average Funding Goals of Previous Projects",
                                       "prev_funding_goal_distribution.png",
                                       "Average Funding Goal ($)")
            
        # Pledged amount of previous projects distribution
        if pledged_prev_stats["values"]:
            plot_numerical_distribution(pledged_prev_stats["values"],
                                       "Distribution of Pledged Amounts of Previous Projects",
                                       "prev_pledged_distribution.png",
                                       "Average Pledged Amount ($)")
            
    except json.JSONDecodeError:
        print(f"Error: {json_file} is not a valid JSON file!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 