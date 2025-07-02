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

def get_solved_contest_problems(handle):
    submissions = get_user_submissions(handle)['result']
    contests = get_user_contests(handle)
    solved_problems = defaultdict(set)
    for submission in submissions:
        if submission['verdict'] == 'OK':
            contest_id = submission['contestId']
            problem = submission['problem']
            solved_problems[contest_id].add(problem['index'])

    contest_solved = defaultdict(set)
    for contest in contests:
        contest_id = contest['contestId']
        contest_solved[contest_id] = solved_problems[contest_id]
    return contest_solved

def get_unsolved_contest_problems(handle):
    submissions = get_user_submissions(handle)['result']
    contests = get_user_contests(handle)
    unsolved_problems = defaultdict(set)
    for submission in submissions:
        if submission['verdict'] != 'OK':
            contest_id = submission['contestId']
            problem = submission['problem']
            unsolved_problems[contest_id].add(problem['index'])

    contest_unsolved = defaultdict(set)
    for contest in contests:
        contest_id = contest['contestId']
        contest_unsolved[contest_id] = unsolved_problems[contest_id]
    return contest_unsolved

def get_user_info(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        user = data['result'][0]
        current_rating = user['rating']
        max_rating = user['maxRating']
        current_rank = user['rank']
        max_rank = user['maxRank']
        avatar = user['avatar']
        return {
            'current_rating': current_rating,
            'max_rating': max_rating,
            'current_rank': current_rank,
            'max_rank': max_rank,
            'avatar': avatar
        }
    return None, None, None, None, None