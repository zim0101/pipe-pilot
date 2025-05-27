#!/usr/bin/env python3
"""
Jenkins AI Agent - Main Entry Point
Generates Jenkins pipelines using AI and local repository analysis
"""


def print_ascii_banner():
    """Print cool ASCII art banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗ ██╗██████╗ ███████╗    ██████╗ ██╗██╗      ██████╗ ████████╗        ║
║   ██╔══██╗██║██╔══██╗██╔════╝    ██╔══██╗██║██║     ██╔═══██╗╚══██╔══╝        ║
║   ██████╔╝██║██████╔╝█████╗      ██████╔╝██║██║     ██║   ██║   ██║           ║
║   ██╔═══╝ ██║██╔═══╝ ██╔══╝      ██╔═══╝ ██║██║     ██║   ██║   ██║           ║
║   ██║     ██║██║     ███████╗    ██║     ██║███████╗╚██████╔╝   ██║           ║
║   ╚═╝     ╚═╝╚═╝     ╚══════╝    ╚═╝     ╚═╝╚══════╝ ╚═════╝    ╚═╝           ║
║                                                                               ║
║              🚀 AI-Powered Jenkins Pipeline Generator 🚀                      ║
║                                                                               ║
║   ┌─────────────────────────────────────────────────────────────────────┐     ║
║   │  ⚡ Clone & Analyze → 🤖 AI Generation → 🔄 Git Push → 🏗️ Jenkins    │     ║
║   │                                                                     │     ║
║   │  ✅ SSH Detection    ✅ Plugin Management   ✅ Full Automation      │     ║
║   │  ✅ Multi-Language   ✅ Interactive Mode    ✅ Production Ready     │     ║
║   └─────────────────────────────────────────────────────────────────────┘     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

"""
    print(banner)


import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = Path(__file__).parent
env_path = root_dir / ".env"
load_dotenv(env_path)

# Add src directory to Python path
sys.path.insert(0, str(root_dir / "src"))

from agent import JenkinsAIAgent


def main():
    """Main entry point for Jenkins AI Agent"""

    # Print the cool banner first
    print_ascii_banner()

    if len(sys.argv) < 2:
        print("Usage: python main.py <github_repo_url> [model_override]")
        print("\nExamples:")
        print("  python main.py https://github.com/user/repo")
        print(
            "  python main.py https://github.com/user/repo anthropic/claude-3.5-sonnet")
        print("\nCommands:")
        print("  python main.py --help            # Show this help")
        print("\nFeatures:")
        print("  ✅ Local git clone analysis (no GitHub API dependency)")
        print("  ✅ Automatic Jenkins CLI download and plugin detection")
        print("  ✅ Smart plugin detection (only uninstalled plugins)")
        print("  ✅ Interactive pipeline improvements")
        print(
            "  ✅ Full automation: Git push + Job creation + Plugin installation")
        print("  ✅ Production-ready output files")
        print("\nSetup: Set OPENROUTER_API_KEY and AI_MODEL in .env file")
        print("Get API key: https://openrouter.ai")
        print("\nSupported models:")
        print("  • anthropic/claude-3-haiku        (fast & cheap)")
        print("  • anthropic/claude-3.5-sonnet     (best quality)")
        print("  • openai/gpt-4o                   (alternative)")
        print("  • meta-llama/llama-3.1-8b-instruct:free (free tier)")
        sys.exit(1)

    # Handle special commands
    if sys.argv[1] in ["--help", "-h"]:
        main()  # Show help and exit
        return

    # Debug: Check .env file status
    print(f"🔍 Environment Debug:")
    print(f"   Script location: {root_dir}")
    print(f"   .env file path: {env_path}")
    print(f"   .env exists: {'✅' if env_path.exists() else '❌'}")

    if env_path.exists():
        print(f"   .env file size: {env_path.stat().st_size} bytes")
        # Check if OPENROUTER_API_KEY is in the file (without showing the actual key)
        env_content = env_path.read_text()
        has_openrouter_key = "OPENROUTER_API_KEY" in env_content
        print(
            f"   Contains OPENROUTER_API_KEY: {'✅' if has_openrouter_key else '❌'}")

    # Check for required environment variables
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    print(f"   OPENROUTER_API_KEY loaded: {'✅' if openrouter_key else '❌'}")

    if not openrouter_key:
        if not openrouter_key:
            print("❌ Missing OPENROUTER_API_KEY environment variable")
            print("1. Get API key from: https://openrouter.ai")
            print("2. Add to .env file: OPENROUTER_API_KEY=your_key_here")
            sys.exit(1)

    # Get AI model from environment
    ai_model = os.getenv('AI_MODEL', 'anthropic/claude-3-haiku')
    print(f"   AI Model: {ai_model}")

    # Allow command line override of model
    if len(sys.argv) > 2:
        ai_model = sys.argv[2]
        print(f"   AI Model (override): {ai_model}")

    # Show Jenkins configuration status
    jenkins_url = os.getenv('JENKINS_URL', 'http://localhost:8080')
    jenkins_user = os.getenv('JENKINS_USERNAME', 'admin')
    jenkins_token = os.getenv('JENKINS_TOKEN')

    print(f"\n🔧 Jenkins Configuration:")
    print(f"   URL: {jenkins_url}")
    print(f"   Username: {jenkins_user}")
    print(
        f"   Token: {'✅ Set' if jenkins_token else '❌ Not set (will try without auth)'}")

    repo_url = sys.argv[1]

    try:
        # Initialize agent
        agent = JenkinsAIAgent(ai_model)

        # Generate initial files
        success = agent.initialize_project(repo_url)

        if not success:
            sys.exit(1)

        # Interactive feedback loop
        print(
            f"\n💬 Interactive Mode - Provide feedback to improve the pipeline")
        print(f"   Type 'exit' or 'quit' to finish")
        print(
            f"   Type 'ready' to start automation (git push + job creation + plugins)")
        print(f"   Type 'help' for examples")

        while True:
            try:
                feedback = input(
                    f"\n📝 Your feedback (or 'exit'/'ready'): ").strip()

                if feedback.lower() in ['exit', 'quit', 'done']:
                    print("✅ Pipe Pilot session completed!")
                    break

                if feedback.lower() == 'ready':
                    print("🚀 Starting automation phase...")
                    automation_success = agent.start_automation()
                    if automation_success:
                        print("\n🎉 Full automation completed successfully!")
                        print("   ✅ Jenkinsfile committed and pushed")
                        print("   ✅ Jenkins job created")
                        print("   ✅ Required plugins installed")
                        print("\n🏁 Your Jenkins pipeline is ready to use!")
                        print("🔗 Don't forget to set up GitHub webhook:")
                        print(f"   Payload URL: {jenkins_url}/github-webhook/")
                    else:
                        print("\n⚠️ Automation completed with some issues")
                        print("   Please check the logs above for details")
                    break

                if feedback.lower() == 'help':
                    print(f"\n💡 Example feedback:")
                    print(f"   • 'Add Docker build stage'")
                    print(f"   • 'Remove testing stage'")
                    print(f"   • 'Add SonarQube code analysis'")
                    print(f"   • 'Change build retention to 5 builds'")
                    print(f"   • 'Add Slack notifications'")
                    print(f"   • 'Use Maven instead of Gradle'")
                    print(f"   • 'Enable GitHub hook trigger for SCM polling'")
                    print(f"\n🚀 When ready to deploy:")
                    print(f"   • Type 'ready' to start full automation")
                    continue

                if not feedback:
                    continue

                # Process feedback
                success = agent.modify_project(feedback)

                if not success:
                    print("❌ Failed to process feedback. Try again.")

            except KeyboardInterrupt:
                print("\n\n✅ Pipe Pilot session completed!")
                break
            except EOFError:
                print("\n\n✅ Pipe Pilot session completed!")
                break

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()