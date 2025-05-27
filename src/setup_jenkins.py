"""
Jenkins Context Setup Utility
Automatic setup for Jenkins plugin detection using .env credentials
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

# Add src directory to path
sys.path.insert(0, str(root_dir / "src"))

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jenkins_cli import JenkinsCLIHelper, create_jenkins_context_file


def setup_jenkins_context() -> bool:
    """Automatic setup for Jenkins context using .env credentials"""

    print("🔧 Jenkins Context Setup (Automatic)")
    print("=" * 45)

    # Get Jenkins connection details from environment
    jenkins_url = os.getenv('JENKINS_URL', 'http://localhost:8080')
    username = os.getenv('JENKINS_USERNAME', 'admin')
    token = os.getenv('JENKINS_TOKEN')
    cli_jar = os.getenv('JENKINS_CLI_JAR', './jenkins-cli.jar')

    print(f"📡 Jenkins URL: {jenkins_url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Token: {'✅ Set' if token else '❌ Not set'}")
    print(f"📦 CLI jar: {cli_jar}")

    # Test connection and create context
    try:
        cli_helper = JenkinsCLIHelper(jenkins_url, username, token, cli_jar)

        # Test basic connectivity
        version_info = cli_helper.get_jenkins_version()
        if version_info:
            print(f"✅ Jenkins connection successful!")
            print(f"   Version: {version_info.get('jenkins_version', 'Unknown')}")

            # Get full context
            success = create_jenkins_context_file("./output")

            if success:
                print(f"🎉 Jenkins context setup complete!")
                print(f"📁 Context saved to: ./output/jenkins_context.json")
                return True
            else:
                print(f"❌ Failed to create Jenkins context")
                return False
        else:
            print(f"❌ Could not connect to Jenkins")
            print(f"💡 Please check:")
            print(f"   - Jenkins is running at {jenkins_url}")
            print(f"   - Username and token are correct in .env file")
            print(f"   - Network connectivity")
            return False

    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False


if __name__ == "__main__":
    success = setup_jenkins_context()

    if not success:
        print(f"\n💡 Jenkins context setup failed")
        print(f"   The agent will still work but may include already installed plugins")