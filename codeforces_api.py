from collections import defaultdict
import requests
import json

def get_user_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)
    data = response.json()
    return data

def get_problem_info(handle):
    data = get_user_submissions(handle)
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

def get_user_contests(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = requests.get(url)
    data = response.json()
    return data['result']

def get_contest_problems(contest_id):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
    response = requests.get(url)
    data = response.json()
    return data['result']['problems']
