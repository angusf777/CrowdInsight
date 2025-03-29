import json
import numpy as np
from typing import Dict, List, Any

def validate_embedding(embedding: List[float], name: str):
    """
    Validates a single embedding vector.
    
    embedding: List of float values representing the embedding
    name: Name of the embedding for error messages
        
    Returns:
        List of error messages, empty if no issues found
    """
    errors = []
    
    # Check if embedding is empty
    if not embedding:
        errors.append(f"{name} is empty")
        return errors
    
    # Convert to numpy array for easier analysis
    embedding_array = np.array(embedding)
    
    # Check if all values are zero
    if np.all(embedding_array == 0):
        errors.append(f"{name} contains all zeros")
    
    # Check if all values are the same
    if np.all(embedding_array == embedding_array[0]):
        errors.append(f"{name} contains all identical values")
    
    # Check for NaN or infinite values
    if np.any(np.isnan(embedding_array)) or np.any(np.isinf(embedding_array)):
        errors.append(f"{name} contains NaN or infinite values")
    
    # Check if variance is extremely low (might indicate poor embedding)
    if np.var(embedding_array) < 1e-6:
        errors.append(f"{name} has very low variance")
    
    return errors

def validate_campaign_embeddings(campaign: Dict[str, Any]):
    """
    Validates all embeddings in a single campaign.
    
    campaign: Dictionary containing campaign data
        
    Returns:
        List of error messages, empty if no issues found
    """
    errors = []
    
    # List of embedding fields to validate
    embedding_fields = [
        'description_embedding',
        'blurb_embedding',
        'risk_embedding',
        'category_embedding',
        'subcategory_embedding',
        'country_embedding'
    ]
    
    # Validate each embedding
    for field in embedding_fields:
        if field not in campaign:
            errors.append(f"Missing {field}")
            continue
            
        field_errors = validate_embedding(campaign[field], field)
        errors.extend(field_errors)
    
    return errors

def validate_processed_campaigns(file_path: str):
    """
    Validates embeddings in all campaigns from the JSON file.
    
    file_path: Path to the processed campaigns JSON file
        
    Returns:
        Dictionary mapping campaign IDs to lists of error messages
    """
    validation_results = {}
    
    try:
        with open(file_path, 'r') as f:
            campaigns = json.load(f)
            
        if not isinstance(campaigns, list):
            return {"file_error": ["JSON file does not contain a list of campaigns"]}
            
        for campaign in campaigns:
            if 'id' not in campaign:
                continue
                
            campaign_id = campaign['id']
            errors = validate_campaign_embeddings(campaign)
            
            if errors:
                validation_results[campaign_id] = errors
                
    except Exception as e:
        return {"file_error": [f"Error reading or processing file: {str(e)}"]}
    
    return validation_results

def main():
    
    file_path = r"C:\Users\qjona\OneDrive\Desktop\Year 4 Sem 2\FYP Sem 2\Project Code\1000processed.json"

    # Validate all campaigns
    results = validate_processed_campaigns(file_path)
    
    if not results:
        print("All embeddings passed validation")
    else:
        num_problematic_campaigns = len(results)
        print(f"\nFound {num_problematic_campaigns} campaigns with issues:")
        for campaign_id, errors in results.items():
            print(f"\nCampaign {campaign_id}:")
            for error in errors:
                print(f"  - {error}")

if __name__ == "__main__":
    main()