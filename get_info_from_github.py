import requests
import re
from collections import defaultdict
import networkx as nx

def get_pr_info(repo, access_token, number_of_pages=20):
    # GET /repos/:owner/:repo/issues/comments
    prs = []
    url = "https://api.github.com/repos/edx/{}/pulls?per_page=100&page={}&access_token={}&state=all"
    for page in range(1, number_of_pages + 1):
        print "getting page {} of {}...".format(page, number_of_pages)
        r = requests.get(url.format(repo, page, access_token))
        for pr in r.json():
            if pr['body'] is None:
                tagged = []
            else:
                tagged = [person.strip("@") for person in re.findall(r"@[\w\d-]+", pr['body'])]
            prs.append({
                "user": pr['user']['login'],
                "number": pr['number'],
                "created_at": pr['created_at'],
                "closed_at": pr['closed_at'],
                'merged_at': pr['merged_at'],
                "body": pr['body'],
                "tagged": tagged,
                "repo": repo,
            })

    return prs


def get_contributers(repo, access_token):
    url = "https://api.github.com/repos/edx/{}/contributors?per_page=500&page={}&access_token={}"
    contributers = []
    for page in [1,2,3]:
        r = requests.get(url.format(repo, page, access_token))
        for user in r.json():
            contributers.append(user['login'])

    return contributers


def make_graph(contributers):
    G = nx.DiGraph()
    G.add_nodes_from(contributers)
    for pr in prs:
        user = pr['user']
        for tagged in pr['tagged']:
            if tagged in contributers:
                if not G.has_edge(user, tagged):
                    G.add_weighted_edges_from([(user, tagged, 1)])
                else:
                    G[user][tagged]['weight'] += 1
    return G
