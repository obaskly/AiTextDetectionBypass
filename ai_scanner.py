import requests
import json
import os
import time

def detect_ai_in_text(api_key, text):
    url = "https://ai-detect.undetectable.ai/detect"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'key': api_key,
        'model': 'detector_v2'
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("Response:", response.text)  # Print the response for more details
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None

def get_detection_result(api_key, document_id):
    url = "https://ai-detect.undetectable.ai/query"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {'id': document_id}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while querying: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred while querying: {req_err}")
        return None

def scan_text_for_ai(api_key, text):
    # Detect AI in the text
    detection_response = detect_ai_in_text(api_key, text)
    
    if detection_response is None or detection_response.get("status") != "pending":
        print("Failed to detect AI in text.")
        return None, None
    
    # Get the document ID from the response
    document_id = detection_response.get("id")
    if not document_id:
        print("No document ID returned from detection.")
        return None, None

    print("Detection is processing... querying result now.")
    
    max_retries = 10  # Maximum number of retries (for 30 seconds total if checking every 3 seconds)
    retries = 0
    
    # Poll the result every 3 seconds until it's ready
    while retries < max_retries:
        result_response = get_detection_result(api_key, document_id)

        if result_response and result_response.get("status") == "done":
            result_details = result_response.get("result_details")
            if result_details:
                human_percentage = result_details.get("human", 0)
                ai_percentage = 100 - human_percentage
                
                # Collect individual detector results
                detector_results = {}
                for detector, score in result_details.items():
                    if detector != "human":  # Skip the human score
                        human_score = 100 - score  # Calculate human percentage
                        detector_results[detector] = {
                            "ai_percentage": score,
                            "human_percentage": human_score
                        }

                return ai_percentage, detector_results
            else:
                print("No result details available.")
                return None, None

        elif result_response:
            print("Detection still pending... retrying in 3 seconds...")
            time.sleep(3)  # Wait for 3 seconds before retrying
            retries += 1
        else:
            print("Failed to query the result.")
            return None, None

    print("Max retries reached. The document is still processing.")
    return None, None

def scan_text(api_key, text):
    return scan_text_for_ai(api_key, text)
