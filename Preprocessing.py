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
    
        try:
            # Get description from the campaign
            text = campaign.get("description", '')
            
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

            return embedding[0] # Return the single embedding array
        
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

    #def process_target_variable(self, campaign: Dict):
        #return campaign.get('state') == 'successful'
    

    def process_campaign(self, campaign: Dict, idx: int):
        return {
            'id': campaign.get('id', str(idx)),
            'description_embedding': self.process_description_embedding(campaign, idx).tolist(),
            'risk_embedding': self.process_riskandchallenges_embedding(campaign, idx).tolist(),
            'image_count': int(campaign['image_count']) if 'image_count' in campaign else 0,  # Access from campaign
            'video_count': int(campaign['video_count']) if 'video_count' in campaign else 0,  # Access from campaign
        }

def main():
    # Load campaign data
    file_path = r"C:\Users\qjona\OneDrive\Desktop\Year 4 Sem 2\FYP Sem 2\Project Code\project_descriptions.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        campaigns = json.load(file)

    # Initialize processor with embeddings
    processor = CampaignProcessor(data=campaigns)  # final_embeddings from your previous code
    
    # Process all campaigns
    processed_campaigns = []
    for idx, campaign in enumerate(campaigns):
        processed_campaign = processor.process_campaign(campaign, idx)

        # Add the processed campaign to our list
        processed_campaigns.append(processed_campaign)
    
    #store the data to MongoDB
    cluster = MongoClient("mongodb+srv://qjonathan928:<urpassword>@cluster0.j9fad.mongodb.net/")
    db = cluster['KickstarterProject'] 
    collection = db['campaigns']  

    # Insert processed campaigns into MongoDB
    collection.insert_many(processed_campaigns)

if __name__ == "__main__":
    main()