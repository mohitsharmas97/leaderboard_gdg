import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import time
from datetime import datetime

def get_badge_dates(url):
    """
    Scrapes a Google Cloud Skills Boost public profile for badge earned dates.
    Returns a dictionary mapping badge titles to their earned dates.
    """
    print(f"Scraping profile page for dates: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not scrape page for dates. Date column will be empty. {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    badge_elements = soup.find_all('div', class_='profile-badge')
    
    dates_map = {}
    for badge in badge_elements:
        title_element = badge.find('span', class_='ql-title-medium')
        date_element = badge.find('span', class_='ql-body-medium')
        
        if title_element and date_element:
            title = title_element.text.strip()
            date = date_element.text.strip().replace("Earned ", "", 1)
            dates_map[title] = date
            
    return dates_map

def parse_date(date_str):
    """
    Parses various date formats into a datetime object.
    Handles formats like "Dec 31, 2024", "Jan 1, 2025", or "Oct 4, 2025 EDT"
    """
    if not date_str or date_str == 'N/A':
        return None
    
    try:
        # Remove "Earned " prefix if present
        date_str = date_str.replace("Earned ", "").strip()
        
        # Remove timezone suffixes (EDT, EST, PST, etc.)
        date_str = date_str.replace(" EDT", "").replace(" EST", "").replace(" PDT", "").replace(" PST", "").replace(" CDT", "").replace(" CST", "").replace(" MDT", "").replace(" MST", "").strip()
        
        # Handle double spaces
        date_str = " ".join(date_str.split())
        
        return datetime.strptime(date_str, "%b %d, %Y")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%B %d, %Y")
        except ValueError:
            print(f"Warning: Could not parse date: {date_str}")
            return None

def calculate_completion_time(skill_badges, arcade_badges, dates_map):
    """
    Calculates when a user completed the challenge (reached 20 total).
    Returns the date of the 20th badge/game earned, or None if not completed.
    """
    all_items = []
    
    # Collect all badges with their dates
    for badge in skill_badges:
        name = badge.get('name', '')
        date_str = dates_map.get(name, 'N/A')
        date_obj = parse_date(date_str)
        if date_obj:
            all_items.append({'name': name, 'date': date_obj, 'date_str': date_str})
    
    for badge in arcade_badges:
        name = badge.get('name', '')
        date_str = dates_map.get(name, 'N/A')
        date_obj = parse_date(date_str)
        if date_obj:
            all_items.append({'name': name, 'date': date_obj, 'date_str': date_str})
    
    # Sort by date (earliest first)
    all_items.sort(key=lambda x: x['date'])
    
    # If they have 20 or more items with dates, return the 20th item's date
    if len(all_items) >= 20:
        completion_item = all_items[19]  # 0-indexed, so 19 is the 20th item
        print(f"  Completion reached on: {completion_item['date_str']} (Badge: {completion_item['name']})")
        return completion_item['date_str']
    
    return None

def get_arcade_api_data(profile_url):
    """
    Gets Google Cloud Arcade data by calling the arcadecalc backend API.
    Returns the parsed JSON data from the API.
    """
    api_url = "https://arcadecalc-v1-backend.onrender.com/api/v1/analyzeProfile"
    payload = {"publicUrl": profile_url}
    headers = {
        "source": "lsqQXcYhauLsRDp",
        "Origin": "https://arcadecalc.netlify.app",
        "Referer": "https://arcadecalc.netlify.app/"
    }
    
    print(f"Sending profile URL to Arcade API: {api_url}")

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not retrieve data from the API. {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the API response.")
        return None

def save_detailed_csv(data, filename="google_cloud_badges_details.csv"):
    """
    Saves a detailed list of all badges with their title, date, and points.
    """
    if not data:
        print("No detailed data to save.")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Profile URL', 'Badge Title', 'Date Earned', 'Points'])
            writer.writerows(data)
        print(f"Successfully saved detailed badge data to {filename}")
    except IOError as e:
        print(f"Error: Could not write to file {filename}. {e}")

def save_summary_csv(data_list, filename="google_cloud_profile_summary.csv"):
    """
    Saves the profile summary data with completion time.
    """
    if not data_list:
        print("No summary data to save.")
        return

    try:
        header = [
            'User Name', 'Email', 'Google Cloud Skills Boost Profile URL', 'Access', 'UR', 'Co',
            '# of Skill Badges Completed', 'Names of Skill Badges',
            '# of Arcade Games', 'Names of Completed Arcade Games',
            'Completion Time'  # NEW COLUMN
        ]
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data_list)
        print(f"Successfully saved profile summary to {filename}")
    except IOError as e:
        print(f"Error: Could not write to file {filename}. {e}")

def save_failed_csv(data_list, filename="failed_profiles.csv", fieldnames=None):
    """
    Saves the profiles that failed to process back into a CSV file.
    """
    if not data_list:
        print("No failed profiles to save.")
        return

    if not fieldnames and data_list:
        fieldnames = data_list[0].keys()
    elif not fieldnames:
        print("Error: Cannot save failed profiles, no fieldnames provided.")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"Successfully saved {len(data_list)} failed profiles to {filename}")
    except IOError as e:
        print(f"Error: Could not write to file {filename}. {e}")

def create_sample_input_file(filename):
    """Creates a sample input CSV file if it doesn't already exist."""
    if not os.path.exists(filename):
        print(f"Creating sample input file: {filename}")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['User Name', 'Email', 'Google Cloud Skills Boost Profile URL', 'Access', 'UR', 'Co'])
            writer.writerow(['Sample User', '', 'https://www.cloudskillsboost.google.com/public_profiles/01fa1e14-9949-434b-86dc-0e2ccd3ae339', 'wn All Good', 'Yes', 'No'])
        print("Sample file created. Please add more profile URLs to it.")

# --- Main execution ---
if __name__ == "__main__":
    input_filename = "failed_profiles.csv"
    summary_output_filename = "progress_data_failed.csv"
    detailed_output_filename = "google_cloud_badges_details_failed.csv"
    failed_output_filename = "failed_profiles.csv"

    create_sample_input_file(input_filename)

    all_summary_data = []
    all_detailed_data = []
    failed_profiles = []

    print(f"\nReading profile URLs from '{input_filename}'...")
    try:
        with open(input_filename, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if 'Google Cloud Skills Boost Profile URL' not in reader.fieldnames:
                raise KeyError(f"Input file '{input_filename}' must contain a 'Google Cloud Skills Boost Profile URL' column.")
            
            input_fieldnames = reader.fieldnames

            for i, row in enumerate(reader):
                profile_url = row.get('Google Cloud Skills Boost Profile URL', '').strip()
                if not profile_url:
                    print(f"Skipping empty profile URL in row {i+2}.")
                    continue
                
                print(f"\n--- Processing profile {i+1}: {profile_url} ---")
                
                api_data = get_arcade_api_data(profile_url)
                
                if api_data:
                    dates_map = get_badge_dates(profile_url)
                    try:
                        user_details = api_data.get('data', {}).get('userDetails', {})
                        user_name_from_api = user_details.get('name', '')
                        
                        badges_overview = api_data.get('data', {}).get('badgesOverview', {})
                        skill_badges = badges_overview.get('skillBadges', {}).get('badges', [])
                        
                        arcade_badges = []
                        arcade_categories = ['baseCampBadges', 'levelBadges', 'triviaBadges', 'specialBadges']
                        for category in arcade_categories:
                            arcade_badges.extend(badges_overview.get(category, {}).get('badges', []))

                        # Calculate completion time
                        completion_time = calculate_completion_time(skill_badges, arcade_badges, dates_map)

                        summary_data = {
                            'User Name': row.get('User Name') or user_name_from_api,
                            '# of Skill Badges Completed': len(skill_badges),
                            'Names of Skill Badges': ', '.join([b.get('name', '') for b in skill_badges]),
                            '# of Arcade Games': len(arcade_badges),
                            'Names of Completed Arcade Games': ', '.join([b.get('name', '') for b in arcade_badges]),
                            'Completion Time': completion_time or ''  # NEW FIELD
                        }
                        
                        full_summary_row = row.copy()
                        full_summary_row.update(summary_data)
                        all_summary_data.append(full_summary_row)
                        
                        all_badges_from_api = skill_badges + arcade_badges
                        for badge in all_badges_from_api:
                            name = badge.get('name', 'N/A')
                            points = badge.get('point', 0)
                            date = dates_map.get(name, 'N/A')
                            all_detailed_data.append([profile_url, name, date, points])

                    except (AttributeError, KeyError) as e:
                        print(f"Error processing API data for {profile_url}. Adding to failed list. Details: {e}")
                        failed_profiles.append(row)
                else:
                    print(f"Could not retrieve API data for profile: {profile_url}. Adding to failed list.")
                    failed_profiles.append(row)
                
                time.sleep(1) 

        save_summary_csv(all_summary_data, summary_output_filename)
        save_detailed_csv(all_detailed_data, detailed_output_filename)
        save_failed_csv(failed_profiles, failed_output_filename, input_fieldnames)
        print("\nAll profiles processed.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found. A sample file has been created for you.")
    except KeyError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")