import requests
from urllib.parse import urljoin
import json
from collections import defaultdict

class BitbucketAnalyzer:
    def __init__(self):
        self.base_url = "https://your.stash.instance.com"  # Replace with your actual Bitbucket URL
        self.headers = {
            'Authorization': 'Bearer your_token_here',  # Replace with your actual token
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

    def get_repo_size(self, owner_slug, repo_slug, is_user_repo=True):
        """Get repository statistics including size"""
        if is_user_repo:
            url = f"{self.base_url}/rest/api/1.0/users/{owner_slug}/repos/{repo_slug}/sizes"
        else:
            url = f"{self.base_url}/rest/api/1.0/projects/{owner_slug}/repos/{repo_slug}/sizes"
        
        # Add headers to simulate interactive request
        size_headers = {
            **self.headers,
            'X-Requested-With': 'XMLHttpRequest',
            'X-Atlassian-Token': 'no-check',
            'Content-Type': 'application/json'
        }
        
        params = {'forceCalculation': 'true'}
        
        try:
            # First request to trigger calculation
            response = requests.post(url, headers=size_headers, params=params)
            response.raise_for_status()
            
            # Second request to get the result
            response = requests.get(url, headers=size_headers)
            response.raise_for_status()
            size_info = response.json()
            return size_info.get('repository', 0)  # 'repository' field contains the total size
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not get size for repo {repo_slug}: {str(e)}")
            return 0

    def get_repo_owner(self, owner_slug, repo_slug, is_user_repo=True):
        """Get repository owner from permissions"""
        if is_user_repo:
            url = f"{self.base_url}/rest/api/1.0/users/{owner_slug}/repos/{repo_slug}/permissions"
        else:
            url = f"{self.base_url}/rest/api/1.0/projects/{owner_slug}/repos/{repo_slug}/permissions"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            permissions = response.json()
            
            # Look for users with admin permission
            for permission in permissions.get('values', []):
                if permission.get('permission') == 'REPO_ADMIN':
                    user = permission.get('user', {})
                    return user.get('displayName', user.get('name', 'Unknown'))
            
            return owner_slug  # fallback to the owner_slug if no admin found
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not get owner for repo {repo_slug}: {str(e)}")
            return owner_slug

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
                repo_size = self.get_repo_size(project['key'], repo['slug'])
                
                repo_info = {
                    'name': repo['name'],
                    'project_key': project['key'],
                    'slug': repo['slug'],
                    'size_bytes': repo_size
                }
                
                stats['repos_by_owner'][owner].append(repo_info)
                stats['total_size'] += repo_size
                
        return stats

    def analyze_single_repository(self, owner_slug, repo_slug, is_user_repo=True):
        """Analyze a single repository and collect statistics"""
        stats = {}
        
        # Construct URL based on whether it's a user repo (fork) or project repo
        if is_user_repo:
            url = f"{self.base_url}/rest/api/1.0/users/{owner_slug}/repos/{repo_slug}"
        else:
            url = f"{self.base_url}/rest/api/1.0/projects/{owner_slug}/repos/{repo_slug}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        repo_info = response.json()
        
        # Get repository size and owner
        repo_size = self.get_repo_size(owner_slug, repo_slug, is_user_repo)
        repo_owner = self.get_repo_owner(owner_slug, repo_slug, is_user_repo)
        
        stats = {
            'name': repo_info['name'],
            'slug': repo_slug,
            'size_bytes': repo_size,
            'created_date': repo_info.get('createdDate'),
            'owner': repo_owner,
            'is_fork': bool(repo_info.get('origin')),
            'fork_of': repo_info.get('origin', {}).get('name') if repo_info.get('origin') else None
        }
        
        return stats

def main():
    try:
        analyzer = BitbucketAnalyzer()
        
        # Example for analyzing a project repository
        project_key = "PROJECT"  # Replace with actual project key
        repo_slug = "repository"  # Replace with actual repo slug
        
        stats = analyzer.analyze_single_repository(project_key, repo_slug, is_user_repo=False)
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 
