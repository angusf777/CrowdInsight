import json
import re
import os
import pandas as pd
from datetime import datetime


def process_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    # Replace newline characters with spaces
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\r', ' ', text)

    # Remove backslashes when they precede special characters
    text = text.replace('\\\'', '\'').replace('\\"', '"').replace('\\`', '`')
    text = re.sub(r'\\([^\w])', r'\1', text)
    
    # Extract the first sentence (assumes sentences end with a period)
    first_sentence = text.split('.')[0] + '.' if '.' in text else text.strip()
    
    # Find the last occurrence of the first sentence
    last_index = text.rstrip().rfind(first_sentence)
    if last_index > 0:  # If found somewhere in the middle, keep the last segment
        return text[last_index:].strip()
    
    return text.strip()

def process_blurb(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    # Replace newline characters with spaces
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\r', ' ', text)

    # Remove backslashes when they precede special characters
    text = text.replace('\\\'', '\'').replace('\\"', '"').replace('\\`', '`')
    text = re.sub(r'\\([^\w])', r'\1', text)
    return text.strip()

def load_json(filepath):
    """ Load JSON file into a dictionary """
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Convert a date string from "dd/mm/yyyy" format to a datetime object
def parse_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y")

def main():
    # Load data
    website_data = load_json("Data/website_database.json")
    project_data = load_json("RawData/project_descriptions_20000.json")
    
    if website_data is None or project_data is None:
        return
    
    large_dict = {entry['id']: entry for entry in website_data}
    processed_data = {}
    
    for project in project_data:
        project_id = project['id']
        if project_id not in large_dict:
            print(f"Missing project in website data: {project}")
            return

        creator_id = project.get("creator_id")
        past_projects = [p for p in website_data if p.get("creator_id") == creator_id and parse_date(p.get("deadline")) < parse_date(large_dict[project_id]["launched_at"])]
        past_success = [p for p in past_projects if p["state"] == "successful"]
        past_failed = [p for p in past_projects if p["state"] == "failed"]
        avg_funding_goal = sum(p["goal_usd"] for p in past_projects) / len(past_projects) if past_projects else 0
        avg_pledged = sum(p["pledged_usd"] for p in past_projects) / len(past_projects) if past_projects else 0

        processed_data[int(project_id)] = {
            "description": process_text(project.get("description", "")),
            "blurb": process_blurb(large_dict[project_id].get("blurb", "")),
            "risk": process_text(project.get("risk", "")),
            "subcategory": project.get("subcategory", ""),
            "category": project.get("category", ""),
            "country": project.get("country", ""),
            "description_length": len(process_text(project.get("description", "")).split()),
            "funding_goal": project.get("goal", 0),
            "image_count": project.get("image_count", 0),
            "video_count": project.get("video_count", 0),
            "campaign_duration": project.get("campaign_duration", 0),
            "previous_projects": len(past_projects),
            "previous_successful_projects": len(past_success),
            "previous_failed_projects": len(past_failed),
            "have_previous_project": 1 if past_projects else 0,
            "average_funding_goal": avg_funding_goal,
            "average_pledged": avg_pledged,
            "state": 1 if project.get("state") == "successful" else 0,
        }
    
    # Save processed data
    output_path = "Data/pre_inputdata.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(processed_data, file, indent=4, ensure_ascii=False)
    
    print(f"Processed data saved to {output_path}")


if __name__ == "__main__":
    main()