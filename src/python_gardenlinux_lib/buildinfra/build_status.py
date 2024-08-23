from urllib.request import urlopen
import json

def get_nightly_status():
    github_workflows = [
        {
            'repo': 'gardenlinux',
            'workflow_id': '28837699'
        },
        {
            'repo': 'repo',
            'workflow_id': '84300234'
        },
        {
            'repo': 'repo',
            'workflow_id': '84300233'
        }
    ]

    for workflow in github_workflows:

        with urlopen(f"https://api.github.com/repos/gardenlinux/{workflow['repo']}/actions/workflows/{workflow['workflow_id']}/runs") as response:
            body = json.loads(response.read().decode())
            workflow_run = body['workflow_runs'][0]
            status = workflow_run['status']
            workflow['status'] = status
            conclusion = workflow_run['conclusion']
            workflow['conclusion'] = conclusion

    return json.dumps(github_workflows)


def get_package_builds():
    # todo: needs to take care of pagination https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
    with urlopen('https://api.github.com/orgs/gardenlinux/repos') as repos_response:
        body = json.loads(repos_response.read().decode())
        package_repos = [ repo['name'] for repo in body if repo['name'].startswith('repo-') ]
        for repo in package_repos:
            with urlopen(f'https://api.github.com/repos/gardenlinux/{repo}/actions/workflows') as workflows_response:
                body = json.loads(workflows_response.read().decode())
                workflows = body['workflows']
                w = [w for w in workflows if w['path'] == '.github/workflows/build.yml']
                assert len(w) == 1
                workflow = w[0]
                with urlopen(workflow['url']) as workflow_response:
                    body = json.loads(workflow_response.read().decode())
                    print(body)

