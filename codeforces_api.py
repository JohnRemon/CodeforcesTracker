from collections import defaultdict
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

def get_problem_info(handle):
    data = get_user_info(handle)
    problems = []
    seen_problems = set()
    for item in data['result']:
        if item['verdict'] == 'OK':
            problem = item['problem']
            problem_id = item['id']
            if problem_id not in seen_problems:
                problems.append(problem)
                seen_problems.add(problem_id)
    return problems

def get_problem_tags(handle):
    problems = get_problem_info(handle)
    tag_map = defaultdict(set)
    for problem in problems:
        for tag in problem['tags']:
            tag_map[tag].add(problem['name'])
    return tag_map