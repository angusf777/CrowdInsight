import json
import numpy as np
from typing import Dict, List
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import gc
from pymongo import MongoClient
 

class CampaignProcessor:
    def __init__(self, data):
        self.data = data
        

        self.categories = sorted(list(set(camp.get('category', '') for camp in self.data)))

         # Initialize Longformer model and tokenizer (for processing description)
        model_name = "allenai/longformer-base-4096"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

        risk_model_name = "sentence-transformers/all-minilm-l6-v2"
        self.risk_tokenizer = AutoTokenizer.from_pretrained(risk_model_name)
        self.risk_model = AutoModel.from_pretrained(risk_model_name)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        self.risk_model = self.risk_model.to(self.device)


    
    def process_description_embedding(self, campaign: Dict, idx: int):
        """Process description embedding"""
    
        try:
            # Get description from the campaign
            text = campaign.get("description", '')
            
            description_length = len(text.split())

            # Clear GPU/CPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()

            # Tokenize
            inputs = self.tokenizer(text, 
                                padding=True, 
                                truncation=True, 
                                max_length=4096, 
                                return_tensors="pt")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Get sentence embeddings through mean pooling
            attention_mask = inputs['attention_mask']
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sentence_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            
            # Move to CPU and convert to numpy
            embedding = sentence_embeddings.cpu().numpy()
            
            # Clear some memory
            del inputs, outputs, token_embeddings, sentence_embeddings
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()

            return embedding[0], description_length # Return the single embedding array and length of description
        
        except Exception as e:
            print(f"Error processing description for campaign {idx}: {str(e)}")
            return np.zeros(768)# Return zero vector of appropriate size (768 for base Longformer)
    

    def process_riskandchallenges_embedding(self, campaign: Dict, idx: int):

        try:
            # Get risk text directly from the campaign dictionary
            text = campaign.get("risk", '')
            
            # Clear GPU/CPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()

            # Tokenize
            inputs = self.risk_tokenizer(text, 
                            padding=True, 
                            truncation=True, 
                            max_length=512,  # minilm uses smaller max length
                            return_tensors="pt")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.risk_model(**inputs)
            
            # Get sentence embeddings through mean pooling
            attention_mask = inputs['attention_mask']
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sentence_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
            # Move to CPU and convert to numpy
            embedding = sentence_embeddings.cpu().numpy()
        
            # Clear some memory
            del inputs, outputs, token_embeddings, sentence_embeddings
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()
            
            return embedding[0]

        except Exception as e:
            print(f"Error processing risk statement for campaign {idx}: {str(e)}")
            return np.zeros(384) # Return zero vector of appropriate size for minilm


    def process_category(self, campaign: Dict):
        """Process category using one-hot encoding"""
        try:
            category = campaign.get('category', '')
            # Create one-hot encoded list
            encoding = [1 if cat == category else 0 for cat in self.categories]
            return encoding
            
        except Exception as e:
            print(f"Error processing category: {str(e)}")
            return [0] * len(self.categories)




    def process_subcategory_embedding(self, campaign: Dict, idx: int):
        """Generate 32-dimensional embedding for subcategory"""
        try:
            subcategory = campaign.get('subcategory', '')
            
            # Generate deterministic embedding
            seed = sum(ord(c) for c in subcategory)
            np.random.seed(seed)
            embedding = np.random.normal(0, 1, 32)  # 32 dimensions
            return embedding / np.linalg.norm(embedding)  # Normalize
            
        except Exception as e:
            print(f"Error processing subcategory for campaign {idx}: {str(e)}")
            return np.zeros(32)


    def process_country_embedding(self, campaign: Dict, idx: int):
        """Generate 24-dimensional embedding for country"""
        try:
            country = campaign.get('country', '')
            
            # Generate deterministic embedding
            seed = sum(ord(c) for c in country)
            np.random.seed(seed)
            embedding = np.random.normal(0, 1, 24)  # 24 dimensions
            return embedding / np.linalg.norm(embedding)  # Normalize
            
        except Exception as e:
            print(f"Error processing country for campaign {idx}: {str(e)}")
            return np.zeros(24)
        


    def process_funding_goal(self, campaign: Dict, idx: int):
        """Process funding goal with compression for extreme values"""
        try:
            goal = float(campaign.get('goal', 0))

            #Log1p transformation, it is good for general compression while preserving relative differences
            transformed_goal = np.log1p(goal)
            
            return transformed_goal
            
        except Exception as e:
            print(f"Error processing funding goal for campaign {idx}: {str(e)}")
            return 0.0
    

    def process_state(self, campaign: Dict) -> bool:
        return campaign.get('state') == 'successful'
    

    def process_campaign(self, campaign: Dict, idx: int):
        """Process all features for a single campaign"""

        description_embedding, description_length = self.process_description_embedding(campaign, idx)

        return {
            'id': campaign.get('id', str(idx)),
            'description_embedding': description_embedding.tolist(),
            'description_length': description_length,
            'risk_embedding': self.process_riskandchallenges_embedding(campaign, idx).tolist(),
            'subcategory_embedding': self.process_subcategory_embedding(campaign, idx).tolist(),
            'country_embedding': self.process_country_embedding(campaign, idx).tolist(),
            'funding_goal': self.process_funding_goal(campaign, idx),
            'image_count': int(campaign['image_count']) if 'image_count' in campaign else 0,  
            'video_count': int(campaign['video_count']) if 'video_count' in campaign else 0,
            'campaign_duration': int(campaign['campaign_duration']) if 'campaign_duration' in campaign else 0, 
            'category_embedding': self.process_category(campaign),
            'state': self.process_state(campaign)
        }

def main():
    # Load campaign data
    file_path = r"C:\Users\qjona\OneDrive\Desktop\Year 4 Sem 2\FYP Sem 2\Project Code\CampaignData.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        campaigns = json.load(file)

    # Initialize processor with embeddings
    processor = CampaignProcessor(data=campaigns)  # final_embeddings from previous code
    
    # Process all campaigns
    processed_campaigns = []
    for idx, campaign in enumerate(campaigns):
        processed_campaign = processor.process_campaign(campaign, idx)

        # Add the processed campaign to our list
        processed_campaigns.append(processed_campaign)

    #print(processed_campaigns[0].keys())
    #print(len(processed_campaigns))
    #print(f"description_embedding: {processed_campaigns[0]['description_embedding']}")
    #print(f"description length: {processed_campaigns[0]['description_length']}")
    #print(f"risk_embedding: {processed_campaigns[0]['risk_embedding']}")
    #print(f"Subcategory_embedding: {processed_campaigns[0]['subcategory_embedding']}")
    #print(f"Country_embedding: {processed_campaigns[0]['country_embedding']}")
    #print(f"Funding_goal: {processed_campaigns[0]['funding_goal']}")
    #print(f"campaign_duration: {processed_campaigns[0]['campaign_duration']}")
    #print(f"category_embedding: {processed_campaigns[0]['category_embedding']}")
    #print(f"state: {processed_campaigns[0]['state']}")

    cluster = MongoClient("mongodb+srv://qjonathan928:manchestercity@cluster0.j9fad.mongodb.net/")
    db = cluster['KickstarterProject']
    collection = db['campaigns']

    # Insert processed campaigns into MongoDB
    collection.insert_many(processed_campaigns)


if __name__ == "__main__":
    main()
