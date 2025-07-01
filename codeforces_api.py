import requests
import json

def get_user_info(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    if data['status'] != 'OK':
        return {"status": data['status']}

    return data

def get_problem_info(handle):
    data = get_user_info(handle)
    print(type(data))
    print(json.dumps(data, indent=2))
    problem_names = []
    seen_problem_names = set()
    for item in data['result']:
        if item['verdict'] == 'OK':
            problem_name = item['problem']['name']
            if problem_name not in seen_problem_names:
                problem_names.append(problem_name)
                seen_problem_names.add(problem_name)
    return problem_names
