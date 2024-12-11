import requests

print("Starting...")
url = "https://api.enphaseenergy.com/api/v2"
data = {"key": "value"}  # Replace with your actual data
response = requests.post(url, json=data)

# Print the status code and response content
print(response.status_code)
print(response.json())  # Assuming the response is in JSON format
