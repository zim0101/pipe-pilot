"""
Jenkins CLI Helper
Handles Jenkins CLI operations for plugin detection and version info
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class JenkinsCLIHelper:
    """Helper to interact with Jenkins via CLI"""

    def __init__(self, jenkins_url: Optional[str] = None, username: Optional[str] = None,
                 token: Optional[str] = None, cli_jar: Optional[str] = None):
        self.jenkins_url = jenkins_url or os.getenv('JENKINS_URL', 'http://localhost:8080')
        self.username = username or os.getenv('JENKINS_USERNAME', 'admin')
        self.token = token or os.getenv('JENKINS_TOKEN')
        self.cli_jar = cli_jar or os.getenv('JENKINS_CLI_JAR', './jenkins-cli.jar')

        # Download CLI jar if it doesn't exist
        self._ensure_cli_jar()

    def _ensure_cli_jar(self):
        """Download Jenkins CLI jar if not present"""
        cli_path = Path(self.cli_jar)

        if not cli_path.exists():
            print(f"📥 Downloading Jenkins CLI jar from {self.jenkins_url}/jnlpJars/jenkins-cli.jar")
            try:
                import requests
                response = requests.get(f"{self.jenkins_url}/jnlpJars/jenkins-cli.jar", timeout=30)
                if response.status_code == 200:
                    cli_path.write_bytes(response.content)
                    print(f"✅ Downloaded jenkins-cli.jar to {cli_path}")
                else:
                    print(f"❌ Failed to download CLI jar: {response.status_code}")
                    print(f"💡 Please download manually from: {self.jenkins_url}/manage/cli/")
            except Exception as e:
                print(f"❌ Error downloading CLI jar: {e}")
                print(f"💡 Please download manually from: {self.jenkins_url}/manage/cli/")
        else:
            print(f"✅ Jenkins CLI jar found at: {cli_path}")

    def _run_cli_command(self, command: List[str], timeout: int = 30) -> Optional[str]:
        """Run Jenkins CLI command"""
        if not Path(self.cli_jar).exists():
            print(f"❌ Jenkins CLI jar not found at {self.cli_jar}")
            return None

        cmd = [
            'java', '-jar', self.cli_jar,
            '-s', self.jenkins_url
        ]

        # Add authentication if available
        if self.username and self.token:
            cmd.extend(['-auth', f'{self.username}:{self.token}'])

        cmd.extend(command)

        try:
            print(f"   🔧 Running: {' '.join(command)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"   ❌ CLI command failed (exit {result.returncode}): {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"   ⏰ CLI command timed out after {timeout} seconds")
            return None
        except Exception as e:
            print(f"   ❌ CLI command error: {e}")
            return None

    def get_jenkins_version(self) -> Dict[str, str]:
        """Get Jenkins version information"""
        print(f"📊 Getting Jenkins version info...")

        version_info = {}

        # Get Jenkins version
        version_output = self._run_cli_command(['version'])
        if version_output:
            version_info['jenkins_version'] = version_output
            print(f"   ✅ Jenkins Version: {version_output}")

        # Get system info (includes more details)
        system_info = self._run_cli_command(['groovy', '=', 'println(Jenkins.instance.version + " on " + System.getProperty("java.version"))'])
        if system_info:
            version_info['system_info'] = system_info
            print(f"   ✅ System Info: {system_info}")

        return version_info

    def get_installed_plugins(self) -> Dict[str, str]:
        """Get list of installed plugins with versions"""
        print(f"🔌 Getting installed plugins...")

        plugins = {}

        # Get plugin list
        plugin_output = self._run_cli_command(['list-plugins'])
        if plugin_output:
            for line in plugin_output.split('\n'):
                if line.strip():
                    # Parse plugin line format: "plugin-name (version)"
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        plugin_name = parts[0]
                        # Extract version from parentheses
                        version_part = ' '.join(parts[1:])
                        if '(' in version_part and ')' in version_part:
                            version = version_part.split('(')[1].split(')')[0]
                            plugins[plugin_name] = version

            print(f"   ✅ Found {len(plugins)} installed plugins")
        else:
            print(f"   ⚠️ Could not get plugin list - Jenkins may not be accessible")

        return plugins

    def get_jenkins_context(self) -> Dict:
        """Get comprehensive Jenkins context for AI"""
        print(f"🔍 Gathering Jenkins context...")

        context = {
            'jenkins_accessible': False,
            'version_info': {},
            'installed_plugins': {},
            'plugin_categories': {
                'scm': [],
                'build': [],
                'test': [],
                'notification': [],
                'deployment': [],
                'security': [],
                'ui': []
            }
        }

        # Try to get version info
        version_info = self.get_jenkins_version()
        if version_info:
            context['jenkins_accessible'] = True
            context['version_info'] = version_info

        # Try to get installed plugins
        installed_plugins = self.get_installed_plugins()
        if installed_plugins:
            context['installed_plugins'] = installed_plugins

            # Categorize plugins
            context['plugin_categories'] = self._categorize_plugins(installed_plugins)

        return context

    def _categorize_plugins(self, plugins: Dict[str, str]) -> Dict[str, List[str]]:
        """Categorize plugins by type"""
        categories = {
            'scm': [],
            'build': [],
            'test': [],
            'notification': [],
            'deployment': [],
            'security': [],
            'pipeline': [],
            'ui': []
        }

        # Plugin categorization based on common plugin names
        plugin_mapping = {
            'scm': ['git', 'github', 'bitbucket', 'gitlab', 'subversion', 'mercurial'],
            'build': ['maven', 'gradle', 'nodejs', 'ant', 'msbuild', 'docker'],
            'test': ['junit', 'testng', 'xunit', 'cucumber', 'sonarqube', 'jacoco', 'cobertura'],
            'notification': ['slack', 'email', 'mailer', 'teams', 'discord', 'telegram'],
            'deployment': ['deploy', 'kubernetes', 'aws', 'azure', 'ssh', 'ansible', 'terraform'],
            'security': ['credentials', 'role-strategy', 'matrix-auth', 'ldap', 'saml'],
            'pipeline': ['workflow', 'pipeline', 'build-pipeline', 'delivery-pipeline'],
            'ui': ['blueocean', 'dashboard', 'view', 'theme']
        }

        for plugin_name in plugins.keys():
            plugin_lower = plugin_name.lower()
            categorized = False

            for category, keywords in plugin_mapping.items():
                if any(keyword in plugin_lower for keyword in keywords):
                    categories[category].append(plugin_name)
                    categorized = True
                    break

            if not categorized:
                categories.setdefault('other', []).append(plugin_name)

        return categories


def create_jenkins_context_file(output_dir: str = "./output") -> bool:
    """Create Jenkins context file for AI"""
    try:
        print(f"🚀 Creating Jenkins context for AI...")

        cli_helper = JenkinsCLIHelper()
        context = cli_helper.get_jenkins_context()

        # Save context to file
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        context_file = output_path / "jenkins_context.json"
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)

        print(f"✅ Jenkins context saved to: {context_file}")

        # Print summary
        if context['jenkins_accessible']:
            print(f"\n📊 Jenkins Context Summary:")
            print(f"   🔧 Jenkins Version: {context['version_info'].get('jenkins_version', 'Unknown')}")
            print(f"   🔌 Installed Plugins: {len(context['installed_plugins'])}")

            for category, plugins in context['plugin_categories'].items():
                if plugins:
                    print(f"   📂 {category.title()}: {len(plugins)} plugins")
        else:
            print(f"\n⚠️ Jenkins not accessible - context will be limited")
            print(f"   💡 Make sure Jenkins is running and credentials are correct")

        return True

    except Exception as e:
        print(f"❌ Error creating Jenkins context: {e}")
        return False