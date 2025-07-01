import requests

def get_user_info(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    if data['status'] != 'OK':
        return {"status": data['status']}

    return data

