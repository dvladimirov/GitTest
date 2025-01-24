from atlassian import Bitbucket
import json

class BitbucketAnalyzer:
    def __init__(self):
        self.base_url = "https://your.stash.instance.com"  # Replace with your actual Bitbucket URL
        self.token = "your_token_here"  # Replace with your actual token
        self.bitbucket = Bitbucket(
            url=self.base_url,
            token=self.token
        )

    def analyze_repository(self):
        try:
            # Example values - replace these with your actual values
            project_key = "PROJECT"
            repo_slug = "repository"
            username = "username"  # for fork analysis

            # Get project administrators
            project_admins = self.bitbucket.all_project_administrators()
            
            # Get repository info (both project and user repos)
            project_repo = self.bitbucket.get_repo(project_key, repo_slug)
            user_repo = self.bitbucket.get_user_repos(username, repo_slug)
            
            # Get repository size
            repo_size = self.bitbucket.get_repository_size(project_key, repo_slug)
            
            # Get repository permissions
            repo_permissions = self.bitbucket.get_repository_permissions(project_key, repo_slug)
            
            # Get project permissions
            project_permissions = self.bitbucket.get_project_permissions(project_key)
            
            # Get repository branches
            branches = self.bitbucket.get_branches(project_key, repo_slug)
            
            # Collect all information
            analysis = {
                'project_administrators': project_admins,
                'project_repository': project_repo,
                'user_repository': user_repo,
                'repository_size': repo_size,
                'repository_permissions': repo_permissions,
                'project_permissions': project_permissions,
                'branches': branches
            }
            
            # Save results
            with open('bitbucket_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print("Analysis complete! Results saved to 'bitbucket_analysis.json'")
            
            # Print some key information
            print("\n=== Quick Summary ===")
            print(f"Project Administrators: {len(project_admins)}")
            print(f"Repository Size: {repo_size.get('repository', 0) / (1024*1024):.2f} MB")
            print(f"Number of Branches: {len(branches.get('values', []))}")
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")

def main():
    analyzer = BitbucketAnalyzer()
    analyzer.analyze_repository()

if __name__ == "__main__":
    main() 
