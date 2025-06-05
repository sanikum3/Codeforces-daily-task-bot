import requests
import random


def get_problems(min_rating=0, max_rating=3000):
    url = "https://codeforces.com/api/problemset.problems"
    
    responce = requests.get(url)
    data = responce.json()
    
    if data['status'] != "OK":
        print("ERROR API")
        return []
    
    problems = []
    for problem in data["result"]["problems"]:
        if "rating" in problem and min_rating <= problem["rating"] <= max_rating:
            problems.append({
                "contestId" : problem["contestId"],
                "index": problem["index"],
                "name": problem["name"],
                "rating": problem["rating"],
                "tags": problem["tags"],
                "url": f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
            })
            
    return problems


def get_random_problem(min_rating, max_rating):
    problems = get_problems(min_rating, max_rating)
    return random.choice(problems)