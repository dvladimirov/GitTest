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
        # Example values - replace these with your actual values
        project_key = "PROJECT"
        repo_slug = "repository"
        
        analysis = {}

        # Get repository info
        try:
            repo_info = self.bitbucket.get_repo(project_key, repo_slug)
            analysis['repository_info'] = repo_info
            print("✓ Successfully retrieved repository information")
        except Exception as e:
            print(f"✗ Error getting repository info: {str(e)}")
            analysis['repository_info'] = None

        # Get repository labels
        try:
            repo_labels = self.bitbucket.get_repo_labels(project_key, repo_slug)
            analysis['repository_labels'] = repo_labels
            print("✓ Successfully retrieved repository labels")
        except Exception as e:
            print(f"✗ Error getting repository labels: {str(e)}")
            analysis['repository_labels'] = None

        # Save results
        try:
            with open('bitbucket_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2)
            print("\nAnalysis complete! Results saved to 'bitbucket_analysis.json'")
            
            # Print quick summary of what we got
            print("\n=== Quick Summary ===")
            if analysis['repository_info']:
                print(f"Repository Name: {analysis['repository_info'].get('name', 'N/A')}")
                print(f"Project Key: {analysis['repository_info'].get('project', {}).get('key', 'N/A')}")
            if analysis['repository_labels']:
                print(f"Number of Labels: {len(analysis['repository_labels'])}")
                
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")

def main():
    analyzer = BitbucketAnalyzer()
    analyzer.analyze_repository()

if __name__ == "__main__":
    main() 
