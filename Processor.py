"""
Kickstarter Campaign Feature Processor

This module provides functionality to transform raw Kickstarter campaign data into 
machine learning features suitable for prediction models. It handles textual data
using state-of-the-art embedding techniques and processes numeric data with 
appropriate transformations.

The main class, CampaignProcessor, orchestrates the feature generation pipeline,
converting unstructured campaign data into a structured numerical representation
that captures semantic meaning and relevant campaign attributes.

Usage:
    processor = CampaignProcessor(data=campaigns)
    processed_data = []
    for idx, campaign in enumerate(campaigns):
        processed_campaign = processor.process_campaign(campaign, idx)
        processed_data.append(processed_campaign)

Features generated include:
- Text embeddings (description, blurb, risks) using transformer models
- Category and subcategory encodings
- Country information embeddings
- Funding goal transformations
- Campaign metadata features

Copyright (c) 2025 Qian Yongkun Jonathan
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import gc
import gensim.downloader
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import preprocess_string
#import time


class CampaignProcessor:
    """
    A class for processing Kickstarter campaign data into machine learning features.

    This class handles the transformation of raw campaign data into numerical features
    suitable for machine learning models. It uses various embedding techniques for text
    data and appropriate transformations for numerical data.

    Attributes:
        data (list): List of raw campaign data
        categories (list): Sorted list of unique campaign categories
        tokenizer (AutoTokenizer): Tokenizer for the Longformer model
        model (AutoModel): Longformer model for description processing
        RiskandBlurb_tokenizer (AutoTokenizer): Tokenizer for the MiniLM model
        RiskandBlurb_model (AutoModel): MiniLM model for shorter text processing
        glove (KeyedVectors): Pre-trained GloVe word embeddings
        device (torch.device): Device (CPU/GPU) for model computations

    Methods:
        process_description_embedding: Generates embeddings for campaign descriptions
        process_riskandchallenges_embedding: Generates embeddings for risk statements
        process_blurb: Generates embeddings for campaign blurbs
        process_category: One-hot encodes campaign categories
        process_subcategory_embedding: Generates embeddings for subcategories
        process_country_embedding: Generates embeddings for countries
        process_funding_goal: Transforms funding goals using log transformation
        process_previous_funding_goal: Transforms previous funding goals
        process_previous_pledged: Transforms previous pledged amounts
        calculate_previous_sucess_rate: Calculates success rate of previous campaigns
        process_campaign: Processes all features for a single campaign
    """


    def __init__(self, data):
        self.data = data
        self.categories = sorted(list(set(camp.get('category', '') for camp in self.data)))

         # Initialize Longformer model and tokenizer (for processing description)
        model_name = "allenai/longformer-base-4096"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

        # Initialize minilm model and tokenizer (for processing risk and blurb)
        RiskandBlurb_model_name = "sentence-transformers/all-minilm-l6-v2"
        self.RiskandBlurb_tokenizer = AutoTokenizer.from_pretrained(RiskandBlurb_model_name)
        self.RiskandBlurb_model = AutoModel.from_pretrained(RiskandBlurb_model_name)

        # Load GloVe model for country and subcategory embeddings
        self.glove = gensim.downloader.load('glove-wiki-gigaword-100')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        self.RiskandBlurb_model = self.RiskandBlurb_model.to(self.device)


    
    def process_description_embedding(self, campaign: Dict, idx: int) -> Tuple[np.ndarray, int]:
        """
        Process campaign description text into numerical embeddings using Longformer.

        We use the Longformer model (allenai/longformer-base-4096) to process the 
        description texts, as they are usually very long. This method handles
        tokenization, embedding generation, memory management, and error cases.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Tuple containing:
                - A 768-dimensional vector embedding of the description
                - Integer representing the description length (word count)

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
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
            return np.zeros(768), 0 # Return zero vector of appropriate size (768 for base Longformer)
    

    def process_riskandchallenges_embedding(self, campaign: Dict, idx: int) -> np.ndarray:
        """
        Process campaign risk and challenges text into numerical embeddings using MiniLM.

        We use the MiniLM model (sentence-transformers/all-minilm-l6-v2) to process the
        risk and challenges texts, as it is efficient for shorter text sequences and
        good for semantic similarity tasks.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            A 384-dimensional vector embedding of the risk and challenges text

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
        try:
            text = campaign.get("risk", '')
            
            # Clear GPU/CPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()

            # Tokenize
            inputs = self.RiskandBlurb_tokenizer(text, 
                            padding=True, 
                            truncation=True, 
                            max_length=512,  # minilm uses smaller max length
                            return_tensors="pt")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.RiskandBlurb_model(**inputs)
            
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

    def process_blurb(self, campaign: Dict, idx: int) -> np.ndarray:
        """
        Process campaign blurb text into numerical embeddings using MiniLM.

        We use the MiniLM model (sentence-transformers/all-minilm-l6-v2) to process
        the blurb texts, as it is efficient for shorter text sequences and good for
        semantic similarity tasks.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            A 384-dimensional vector embedding of the blurb text

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
        try:
            text = campaign.get("blurb", '')
            
            # Clear GPU/CPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()

            # Tokenize
            inputs = self.RiskandBlurb_tokenizer(text, 
                            padding=True, 
                            truncation=True, 
                            max_length=512,
                            return_tensors="pt")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.RiskandBlurb_model(**inputs)
            
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
            print(f"Error processing blurb for campaign {idx}: {str(e)}")
            return np.zeros(384) # Return zero vector of appropriate size for minilm





    def process_category(self, campaign: Dict) -> List[int]:
        """
        Process campaign category using one-hot encoding.

        This method converts categorical data into binary vectors where each position
        corresponds to a unique category, with 1 indicating the category of the campaign
        and 0 elsewhere.

        Args:
            campaign: Dictionary containing campaign data

        Returns:
            List of integers (0s and 1s) representing the one-hot encoded category

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
        try:
            category = campaign.get('category', '')
            # Create one-hot encoded list
            encoding = [1 if cat == category else 0 for cat in self.categories]
            return encoding
            
        except Exception as e:
            print(f"Error processing category: {str(e)}")
            return [0] * len(self.categories)  # Return all zeros if error




    def process_subcategory_embedding(self, campaign: Dict, idx: int) -> np.ndarray:
        """
        Process campaign subcategory text into numerical embeddings using GloVe.

        We use the GloVe embeddings (glove-wiki-gigaword-100), which captures 
        semantic relationships between words, to process subcategory text.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            A 100-dimensional vector embedding of the subcategory

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
        try:
            text = campaign.get('subcategory', '').lower().strip()
            
            if not text:
                return np.zeros(100)
            
            # Tokenize the text by simple whitespace split
            tokens = text.split()

            # Get embeddings for all available words
            word_vectors = []
            for word in tokens:
                try:
                    word_vectors.append(self.glove[word])
                except KeyError:
                    continue
            
            if not word_vectors:
                return np.zeros(100)
                
            # Average the word vectors
            return np.mean(word_vectors, axis=0)

        except Exception as e:
            print(f"Error processing subcategory for campaign {idx}: {str(e)}")
            return np.zeros(100)



    def process_country_embedding(self, campaign: Dict, idx: int) -> np.ndarray:
        """
        Process campaign country information into numerical embeddings using GloVe.

        We use the GloVe embeddings (glove-wiki-gigaword-100), which captures 
        semantic relationships between words, to process country names.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            A 100-dimensional vector embedding of the country

        Raises:
            Various exceptions may be caught internally and handled by returning zero vectors
        """
        try:
            text = campaign.get('country', '').lower().strip()
            
            
            if not text:
                return np.zeros(100)
            
            # Tokenize the text by simple whitespace split
            tokens = text.split()
            
            # Get embeddings for all available words
            word_vectors = []
            for word in tokens:
                try:
                    word_vectors.append(self.glove[word])
                except KeyError:
                    continue
            
            if not word_vectors:
                return np.zeros(100)
                
            # Average the word vectors
            return np.mean(word_vectors, axis=0)

        except Exception as e:
            print(f"Error processing country for campaign {idx}: {str(e)}")
            return np.zeros(100)

        
    def process_funding_goal(self, campaign: Dict, idx: int) -> float:
        """
        Process campaign funding goal with logarithmic compression.

        Applies Log1p transformation with base 10 to compress extreme values while
        preserving relative differences between funding goals.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Float representing the transformed funding goal

        Raises:
            Various exceptions may be caught internally and handled by returning zero
        """
        try:
            goal = float(campaign.get('funding_goal', 0))

            #Log1p transformation, it is good for general compression while preserving relative differences
            transformed_goal = np.log1p(goal)/np.log(10)
            
            return transformed_goal
            
        except Exception as e:
            print(f"Error processing funding goal for campaign {idx}: {str(e)}")
            return 0.0
        
    
    def process_previous_funding_goal(self, campaign: Dict, idx: int) -> float:
        """
        Process previous campaign funding goal with logarithmic compression.

        Applies Log1p transformation with base 10 to compress extreme values while
        preserving relative differences between previous funding goals.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Float representing the transformed previous funding goal

        Raises:
            Various exceptions may be caught internally and handled by returning zero
        """
        try:
            previous_goal = float(campaign.get('average_funding_goal', 0))

            #Log1p transformation, it is good for general compression while preserving relative differences
            transformed_goal = np.log1p(previous_goal)/np.log(10)
            
            return transformed_goal
            
        except Exception as e:
            print(f"Error processing previous funding goal for campaign {idx}: {str(e)}")
            return 0.0
        

    def process_previous_pledged(self, campaign: Dict, idx: int) -> float:
        """
        Process previous campaign pledged amount with logarithmic compression.

        Applies Log1p transformation with base 10 to compress extreme values while
        preserving relative differences between previous pledged amounts.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Float representing the transformed previous pledged amount

        Raises:
            Various exceptions may be caught internally and handled by returning zero
        """
        try:
            pledged = float(campaign.get('average_pledged', 0))

            #Log1p transformation, it is good for general compression while preserving relative differences
            transformed_pledge = np.log1p(pledged)/np.log(10)
            
            return transformed_pledge
            
        except Exception as e:
            print(f"Error processing pledge amount for campaign {idx}: {str(e)}")
            return 0.0
    

    def calculate_previous_sucess_rate(self, campaign: Dict, idx: int) -> float:
        """
        Calculate success rate of creator's previous campaigns.

        Computes the ratio of successful previous projects to total previous projects.

        Args:
            campaign: Dictionary containing campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Float between 0.0 and 1.0 representing the previous success rate

        Raises:
            Various exceptions may be caught internally and handled by returning zero
        """
        try:
            previousProjects= float(campaign.get('previous_projects', 0))
            previousSuccessfulProjects = float(campaign.get('previous_successful_projects', 0))
            if previousSuccessfulProjects == 0.0:
                return 0.0
            else:
                previous_success_rate =  previousSuccessfulProjects/ previousProjects
                return  previous_success_rate 
            
        except Exception as e:
            print(f"Error calculating previous success rate")
            return 0.0
    

    def process_campaign(self, campaign: Dict, idx: int) -> Dict[str, Any]:
        """
        Process all features for a single campaign.

        This is the main method that orchestrates the extraction and transformation of
        all features for a campaign, combining text embeddings and numerical features
        into a single dictionary ready for machine learning models.

        Args:
            campaign: Dictionary containing raw campaign data
            idx: Index of the campaign in the dataset (for error reporting)

        Returns:
            Dictionary containing the campaign ID and all processed features

        Raises:
            Various exceptions are handled in the individual processing methods
        """

        description_embedding, description_length = self.process_description_embedding(campaign, idx)

        return {
            'id': campaign.get('id', str(idx)),
            'description_embedding': description_embedding.tolist(),
            'description_length': description_length,
            'blurb_embedding': self.process_blurb(campaign, idx).tolist(),
            'risk_embedding': self.process_riskandchallenges_embedding(campaign, idx).tolist(),
            'category_embedding': self.process_category(campaign),
            'subcategory_embedding': self.process_subcategory_embedding(campaign, idx).tolist(),
            'country_embedding': self.process_country_embedding(campaign, idx).tolist(),
            'funding_goal': self.process_funding_goal(campaign, idx),
            'image_count': int(campaign['image_count']) if 'image_count' in campaign else 0,  # Access from campaign
            'video_count': int(campaign['video_count']) if 'video_count' in campaign else 0,
            'campaign_duration': int(campaign['campaign_duration']) if 'campaign_duration' in campaign else 0,  # Access from campaign
            'previous_projects_count': int(campaign['previous_projects']) if 'previous_projects' in campaign else 0,
            'previous_success_rate': self.calculate_previous_sucess_rate(campaign, idx),
            'previous_pledged': self.process_previous_pledged(campaign, idx),
            'previous_funding_goal': self.process_previous_funding_goal(campaign, idx),
            'state': campaign['state'] if 'state' in campaign else 0
        }

def main():
    """
    Main function to process campaign data and save the results.

    This function:
    1. Loads campaign data from a JSON file
    2. Initializes the CampaignProcessor
    3. Processes all campaigns
    4. Saves the processed data to a new JSON file
    5. Reports processing statistics

    The function includes progress tracking and error handling for the processing pipeline.
    """

    #start_time = time.time()
    
    # Load campaign data
    file_path = "Data/pre_inputdata.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        campaigns_dict = json.load(file)

    # Convert dictionary to list of campaigns, adding ID as a field
    campaigns = []
    for campaign_id, campaign_data in campaigns_dict.items():
        campaign_data["id"] = campaign_id
        campaigns.append(campaign_data)

    # Initialize processor with embeddings
    processor = CampaignProcessor(data=campaigns)  # final_embeddings from your previous code


    # Process all campaigns with progress tracking
    processed_campaigns = []
    total_campaigns = len(campaigns)
    print(f"\nStarting to process {total_campaigns} campaigns...")

    for idx, campaign in enumerate(campaigns):
        print(f"Processing campaign {idx + 1}/{total_campaigns} (ID: {campaign['id']})", end='\r')
        processed_campaign = processor.process_campaign(campaign, idx)

        # Add the processed campaign to our list
        processed_campaigns.append(processed_campaign)


    #-------------------------------------------------------------------------------------------------
    #print(processed_campaigns[0].keys())
    #print(len(processed_campaigns))
    #print(f"description_embedding: {processed_campaigns[0]['description_embedding']}")
    #print(f"description length: {processed_campaigns[0]['description_length']}")
    #print(f"blurb_embedding: {processed_campaigns[0]['blurb_embedding']}")
    #print(f"risk_embedding: {processed_campaigns[0]['risk_embedding']}")
    #print(f"Subcategory_embedding: {processed_campaigns[0]['subcategory_embedding']}")
    #print(f"Country_embedding: {processed_campaigns[0]['country_embedding']}")
    #print(f"Funding_goal: {processed_campaigns[0]['funding_goal']}")
    #print(f"campaign_duration: {processed_campaigns[0]['campaign_duration']}")
    #print(f"category_embedding: {processed_campaigns[0]['category_embedding']}")
    #print(f"image_count: {processed_campaigns[0]['image_count']}")
    #print(f"video_count: {processed_campaigns[0]['video_count']}")
    #print(f"previous_projects_count: {processed_campaigns[0]['previous_projects_count']}")
    #print(f"previous_success_rate: {processed_campaigns[0]['previous_success_rate']}")
    #print(f"previous_pledged: {processed_campaigns[0]['previous_pledged']}")
    #print(f"previous_funding_goal: {processed_campaigns[0]['previous_funding_goal']}")
    #print(f"state: {processed_campaigns[0]['state']}")
    #-------------------------------------------------------------------------------------------------

    output_file_path = "allProcessed.json"
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_campaigns, f, indent=2)
        print(f"Successfully saved processed campaigns to {output_file_path}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")


    #end_time = time.time()
    #execution_time = end_time - start_time
    #print(f"Total execution time: {execution_time:.2f} seconds")
    #print(f"Average time per campaign: {execution_time/len(processed_campaigns):.2f} seconds")

if __name__ == "__main__":
    main()

    