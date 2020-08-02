import argparse

import github
from classroom_tools import github_utils

parser = argparse.ArgumentParser('Create test repositories')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo and workflow permissions'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    help='Template repo used to create student repositories in format: OrgName/RepoName'
)
parser.add_argument(
    '--org_name',
    required=True,
    help='GitHub organization with student repositories (for multiples student repositories)'
)
parser.add_argument(
    '--repo_filter',
    required=True,
    help='Prefix to filter repositories for as given assignment or exercise (for multiples student repositories)'
)
parser.add_argument(
    '--num_repos',
    type=int,
    help='Number of student repositories to create'
)


def student_usernames(n=10):
    return list(
        map(
            lambda i: f'PolyStudent{i}',
            range(1, n + 1)
        )
    )


def create_test_repos(token, org_name, repo_filter, usernames, template_repo_fullname):
    g = github.Github(login_or_token=token)
    try:
        org = g.get_organization(org_name)
    except github.UnknownObjectException:
        print(f'Couldn\'t find org: {org_name}')
    template_repo = github_utils.get_repo(fullname=template_repo_fullname, token=token)
    template_files = list(github_utils.get_files_from_repo(template_repo, path=''))
    for user in usernames:
        repo_name = f'{repo_filter}-{user}'
        try:
            repo = org.get_repo(repo_name)
            for file in github_utils.get_files_from_repo(repo=repo, path=''):
                repo.delete_file(
                    path=file.path,
                    message='Deleted file',
                    sha=file.sha,
                )
            print(f'Updated repo: {repo_name}')
        except github.GithubException:
            repo = org.create_repo(
                name=repo_name
            )
            print(f'Created repo: {repo_name}')
        repo.add_to_collaborators('PolyINF1007', permission='admin')
        repo.add_to_collaborators('StudentTestAccount1', permission='push')
        for file in template_files:
            repo.create_file(
                path=file.path,
                message='Initial commit',
                content=file.decoded_content,
                branch='master'
            )


def main(args):
    print('\n\n' + 'Creating test repositories'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    usernames = student_usernames(n=args.num_repos)
    create_test_repos(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter,
        usernames=usernames,
        template_repo_fullname=args.template_repo_fullname
    )


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
