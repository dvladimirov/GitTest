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

    def analyze_single_repository(self, owner_slug, repo_slug, is_user_repo=True):
        """Analyze a single repository and collect statistics"""
        try:
            if is_user_repo:
                repo_info = self.bitbucket.get_user_repos(owner_slug, repo_slug)
            else:
                repo_info = self.bitbucket.get_repo(owner_slug, repo_slug)

            # Get repository size
            size_info = self.bitbucket.get_repository_size(owner_slug, repo_slug)
            repo_size = size_info.get('repository', 0) if size_info else 0

            # Get repository permissions to find owner
            permissions = self.bitbucket.get_repository_permissions(owner_slug, repo_slug)
            owner = owner_slug
            for user in permissions:
                if user.get('permission') == 'REPO_ADMIN':
                    owner = user.get('user', {}).get('displayName', owner_slug)
                    break

            stats = {
                'name': repo_info['name'],
                'slug': repo_slug,
                'size_bytes': repo_size,
                'created_date': repo_info.get('createdDate'),
                'owner': owner,
                'is_fork': bool(repo_info.get('origin')),
                'fork_of': repo_info.get('origin', {}).get('name') if repo_info.get('origin') else None
            }
            
            return stats
            
        except Exception as e:
            print(f"Error analyzing repository: {str(e)}")
            return None

def main():
    try:
        analyzer = BitbucketAnalyzer()
        
        # Example for analyzing a project repository
        project_key = "PROJECT"  # Replace with actual project key
        repo_slug = "repository"  # Replace with actual repo slug
        
        # Set is_user_repo=True for forks (/users/username/repos/slug)
        # Set is_user_repo=False for project repos (/projects/PROJECT/repos/slug)
        stats = analyzer.analyze_single_repository(project_key, repo_slug, is_user_repo=False)
        
        if stats:
            # Print results
            print("\n=== Repository Analysis Results ===")
            print(f"Repository: {stats['name']}")
            print(f"Owner: {stats['owner']}")
            print(f"Size: {stats['size_bytes'] / (1024*1024):.2f} MB")
            print(f"Created: {stats['created_date']}")
            if stats['is_fork']:
                print(f"Forked from: {stats['fork_of']}")
            
            # Save results to file
            with open('bitbucket_analysis_results.json', 'w') as f:
                json.dump(stats, f, indent=2)
            print("\nResults have been saved to 'bitbucket_analysis_results.json'")
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 
