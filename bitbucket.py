from atlassian import Bitbucket
import json
from datetime import datetime

class BitbucketAnalyzer:
    def __init__(self):
        self.base_url = "https://your.stash.instance.com"  # Replace with your actual Bitbucket URL
        self.username = "your_username"  # Replace with your username
        self.password = "your_password"  # Replace with your password
        self.bitbucket = Bitbucket(
            url=self.base_url,
            username=self.username,
            password=self.password
        )

    def analyze_repo(self):
        try:
            project_key = "PC"
            repo_slug = "deployment-config"
            repo_key = "PC"
            group = "test_proj_support"
            
            # Repository Basic Information
            repo_info = self.bitbucket.get_repo(project_key, repo_slug)
            repo_analysis = {
                'name': repo_info.get('name'),
                'project_key': repo_info.get('project', {}).get('key'),
                'created_date': repo_info.get('created_date'),
                'updated_date': repo_info.get('updated_date'),
                'state': repo_info.get('state'),
                'is_public': repo_info.get('public'),
                'fork_strategy': repo_info.get('forkable')
            }

            # Labels Analysis
            labels = self.bitbucket.get_repo_labels(project_key, repo_slug)
            labels_analysis = {
                'total_labels': len(labels),
                'labels_list': labels
            }

            # Users and Groups Analysis
            users = list(self.bitbucket.get_users(user_filter="username", limit=25, start=0))
            repo_users = list(self.bitbucket.repo_users(project_key, repo_slug, limit=99999, filter_str=None))
            repo_groups = list(self.bitbucket.repo_groups(project_key, repo_slug, limit=99999, filter_str=None))
            group_members = list(self.bitbucket.group_members(group, limit=99999))

            access_analysis = {
                'total_users_with_access': len(repo_users),
                'total_groups_with_access': len(repo_groups),
                'users_with_direct_access': [
                    {
                        'name': user.get('name'),
                        'display_name': user.get('displayName'),
                        'email': user.get('emailAddress'),
                        'active': user.get('active'),
                        'permission': user.get('permission')
                    } for user in repo_users
                ],
                'groups_with_access': [
                    {
                        'group_name': group.get('name'),
                        'permission': group.get('permission')
                    } for group in repo_groups
                ],
                f'{group}_members': [
                    {
                        'name': member.get('name'),
                        'display_name': member.get('displayName'),
                        'active': member.get('active')
                    } for member in group_members
                ]
            }

            # Branch Analysis
            branch_model = self.bitbucket.get_branching_model(project_key, repo_slug)
            branch_analysis = {
                'development_branch': branch_model.get('development', {}).get('branch', {}).get('name'),
                'production_branch': branch_model.get('production', {}).get('branch', {}).get('name'),
                'branch_types': branch_model.get('types'),
                'use_default_reviewers': branch_model.get('default_reviewers', {}).get('enabled', False)
            }

            # Compile Complete Analysis
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            complete_analysis = {
                'analysis_timestamp': timestamp,
                'repository_information': repo_analysis,
                'labels_information': labels_analysis,
                'access_control': access_analysis,
                'branch_management': branch_analysis
            }

            # Generate Report
            self._print_report(complete_analysis)
            
            # Save to file
            with open(f'bitbucket_analysis_{project_key}_{repo_slug}_{timestamp.replace(":", "-")}.json', 'w') as f:
                json.dump(complete_analysis, f, indent=2)
            
            return complete_analysis
            
        except Exception as e:
            print(f"Error during analytics: {str(e)}")
            return None

    def _print_report(self, analysis):
        """Print a formatted report of the analysis"""
        print("\n=== Bitbucket Repository Analysis Report ===")
        print(f"Analysis performed at: {analysis['analysis_timestamp']}\n")

        print("=== Repository Information ===")
        repo_info = analysis['repository_information']
        print(f"Name: {repo_info['name']}")
        print(f"Project Key: {repo_info['project_key']}")
        print(f"Created: {repo_info['created_date']}")
        print(f"Last Updated: {repo_info['updated_date']}")
        print(f"State: {repo_info['state']}")
        print(f"Public: {repo_info['is_public']}")

        print("\n=== Labels ===")
        labels = analysis['labels_information']
        print(f"Total Labels: {labels['total_labels']}")
        if labels['labels_list']:
            print("Applied Labels:")
            for label in labels['labels_list']:
                print(f"  - {label}")

        print("\n=== Access Control ===")
        access = analysis['access_control']
        print(f"Users with Direct Access: {len(access['users_with_direct_access'])}")
        print(f"Groups with Access: {len(access['groups_with_access'])}")
        
        print("\n=== Branch Management ===")
        branch = analysis['branch_management']
        print(f"Development Branch: {branch['development_branch']}")
        print(f"Production Branch: {branch['production_branch']}")
        print(f"Default Reviewers Enabled: {branch['use_default_reviewers']}")

def main():
    analyzer = BitbucketAnalyzer()
    analyzer.analyze_repo()

if __name__ == "__main__":
    main() 
