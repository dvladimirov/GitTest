import requests
from urllib.parse import urljoin
import json
from collections import defaultdict

class BitbucketAnalyzer:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
    def get_all_projects(self):
        """Fetch all projects from Bitbucket"""
        projects = []
        start = 0
        limit = 100
        
        while True:
            url = f"{self.base_url}/rest/api/1.0/projects"
            params = {'start': start, 'limit': limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            projects.extend(data['values'])
            
            if data['isLastPage']:
                break
                
            start = data['nextPageStart']
            
        return projects

    def get_repos_for_project(self, project_key):
        """Fetch all repositories for a specific project"""
        repos = []
        start = 0
        limit = 100
        
        while True:
            url = f"{self.base_url}/rest/api/1.0/projects/{project_key}/repos"
            params = {'start': start, 'limit': limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            repos.extend(data['values'])
            
            if data['isLastPage']:
                break
                
            start = data['nextPageStart']
            
        return repos

    def get_repo_size(self, project_key, repo_slug):
        """Get repository size"""
        url = f"{self.base_url}/users/{project_key}/repos/{repo_slug}/sizes"
        params = {'forceCalculation': 'true'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not get size for repo {repo_slug}: {str(e)}")
            return None

    def analyze_repositories(self):
        """Analyze all repositories and collect statistics"""
        stats = {
            'total_repos': 0,
            'repos_by_owner': defaultdict(list),
            'total_size': 0
        }
        
        projects = self.get_all_projects()
        
        for project in projects:
            print(f"Processing project: {project['key']}")
            repos = self.get_repos_for_project(project['key'])
            
            for repo in repos:
                stats['total_repos'] += 1
                
                # Get repository owner
                owner = repo.get('project', {}).get('owner', {}).get('displayName', 'Unknown')
                
                # Get repository size
                size_info = self.get_repo_size(project['key'], repo['slug'])
                repo_size = size_info.get('repository', 0) if size_info else 0
                
                repo_info = {
                    'name': repo['name'],
                    'project_key': project['key'],
                    'slug': repo['slug'],
                    'size_bytes': repo_size
                }
                
                stats['repos_by_owner'][owner].append(repo_info)
                stats['total_size'] += repo_size
                
        return stats

def main():
    # Configuration
    base_url = input("Enter Bitbucket base URL (e.g., https://bitbucket.company.com): ")
    token = input("Enter your access token: ")
    
    try:
        analyzer = BitbucketAnalyzer(base_url, token)
        stats = analyzer.analyze_repositories()
        
        # Print results
        print("\n=== Repository Analysis Results ===")
        print(f"Total number of repositories: {stats['total_repos']}")
        print(f"Total size of all repositories: {stats['total_size'] / (1024*1024*1024):.2f} GB")
        print("\nRepositories by owner:")
        
        for owner, repos in stats['repos_by_owner'].items():
            print(f"\nOwner: {owner}")
            print(f"Number of repositories: {len(repos)}")
            for repo in repos:
                size_mb = repo['size_bytes'] / (1024*1024)
                print(f"  - {repo['name']} ({repo['project_key']}/{repo['slug']}): {size_mb:.2f} MB")
        
        # Save results to file
        with open('bitbucket_analysis_results.json', 'w') as f:
            json.dump(stats, f, indent=2)
        print("\nResults have been saved to 'bitbucket_analysis_results.json'")
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 
