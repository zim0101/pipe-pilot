"""
Local Repository Analyzer
Clones and analyzes repositories from the local filesystem
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Tuple


class LocalRepositoryAnalyzer:
    """Analyzes cloned repository from local filesystem"""

    def __init__(self, repos_dir: str = "./repos"):
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(exist_ok=True)
        self.ssh_available = self._check_ssh_availability()

    def _check_ssh_availability(self) -> bool:
        """Check if SSH is available and configured for GitHub"""

        print(f"🔐 Checking SSH configuration...")

        try:
            # Check if ssh-agent has keys loaded
            result = subprocess.run(
                ['ssh-add', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            has_ssh_keys = result.returncode == 0 and 'no identities' not in result.stdout.lower()

            if has_ssh_keys:
                print(f"   ✅ SSH keys detected in ssh-agent")
            else:
                print(f"   📝 No SSH keys in ssh-agent, checking ~/.ssh/")

                # Check for common SSH key files
                ssh_dir = Path.home() / '.ssh'
                key_files = ['id_rsa', 'id_ed25519', 'id_ecdsa', 'github_rsa']

                for key_file in key_files:
                    key_path = ssh_dir / key_file
                    if key_path.exists():
                        print(f"   ✅ Found SSH key: {key_file}")
                        has_ssh_keys = True
                        break

            if not has_ssh_keys:
                print(f"   ⚠️ No SSH keys found")
                return False

            # Test SSH connection to GitHub
            print(f"   🧪 Testing SSH connection to GitHub...")
            result = subprocess.run(
                ['ssh', '-T', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no', 'git@github.com'],
                capture_output=True,
                text=True,
                timeout=15
            )

            # GitHub SSH test returns exit code 1 but with success message
            if 'successfully authenticated' in result.stderr:
                print(f"   ✅ SSH connection to GitHub successful")
                return True
            elif 'Permission denied' in result.stderr:
                print(f"   ❌ SSH permission denied - keys may not be configured for GitHub")
                return False
            else:
                print(f"   ⚠️ SSH test inconclusive: {result.stderr[:100]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ SSH test timed out")
            return False
        except FileNotFoundError:
            print(f"   ❌ SSH command not found")
            return False
        except Exception as e:
            print(f"   ⚠️ SSH check error: {e}")
            return False

    def _determine_clone_url(self, repo_url: str) -> Tuple[str, str]:
        """Determine the best URL to use for cloning based on SSH availability"""

        original_url = repo_url

        # Only handle GitHub URLs for now
        if not repo_url.startswith('https://github.com/'):
            return original_url, "original"

        # Extract repo path
        repo_path = repo_url.replace('https://github.com/', '').rstrip('/')
        if not '/' in repo_path:
            return original_url, "original"

        # Generate SSH URL
        ssh_url = f"git@github.com:{repo_path}.git"

        if self.ssh_available:
            print(f"   🔐 SSH available - using SSH URL: {ssh_url}")
            return ssh_url, "ssh"
        else:
            print(f"   🌐 SSH not available - using HTTPS URL: {original_url}")
            print(f"   💡 Consider setting up SSH keys for easier authentication:")
            print(f"      https://docs.github.com/en/authentication/connecting-to-github-with-ssh")
            return original_url, "https"

    def clone_and_analyze(self, repo_url: str) -> Dict:
        """Clone repository locally and analyze files"""

        # Extract repository info from URL
        if repo_url.startswith('https://github.com/'):
            repo_path = repo_url.replace('https://github.com/', '').rstrip('/')
        else:
            repo_path = repo_url.rstrip('/')

        owner, repo_name = repo_path.split('/')
        local_repo_path = self.repos_dir / f"{owner}_{repo_name}"

        print(f"📂 Repository: {owner}/{repo_name}")
        print(f"📁 Local path: {local_repo_path}")

        # Determine best clone URL
        clone_url, url_type = self._determine_clone_url(repo_url)

        # Clone repository
        success = self._clone_repository(clone_url, local_repo_path, url_type)
        if not success:
            # If SSH failed, try HTTPS as fallback
            if url_type == "ssh":
                print(f"   🔄 SSH clone failed, trying HTTPS fallback...")
                https_url = f"https://github.com/{repo_path}"
                success = self._clone_repository(https_url, local_repo_path, "https_fallback")

            if not success:
                raise Exception("Failed to clone repository with both SSH and HTTPS")

        # Analyze local files
        analysis = self._analyze_local_repository(repo_url, owner, repo_name,
                                                  local_repo_path)

        return analysis

    def _clone_repository(self, clone_url: str, local_path: Path, url_type: str) -> bool:
        """Clone repository using git command"""

        # Remove existing directory if it exists
        if local_path.exists():
            print(f"   🗑️ Removing existing clone: {local_path}")
            shutil.rmtree(local_path)

        try:
            print(f"   📥 Cloning repository ({url_type})...")
            print(f"      git clone {clone_url} {local_path}")

            # Run git clone command
            result = subprocess.run(
                ["git", "clone", clone_url, str(local_path)],
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            if result.returncode == 0:
                print(f"   ✅ Repository cloned successfully")

                # If we used SSH, verify the remote URL is set correctly
                if url_type in ["ssh", "https_fallback"]:
                    self._verify_remote_url(local_path, clone_url)

                return True
            else:
                print(f"   ❌ Git clone failed:")
                print(f"      stdout: {result.stdout}")
                print(f"      stderr: {result.stderr}")

                # Specific error messages for common issues
                if "Permission denied" in result.stderr and url_type == "ssh":
                    print(f"   💡 SSH permission denied. Your SSH key may not be added to GitHub.")
                elif "Authentication failed" in result.stderr:
                    print(f"   💡 Authentication failed. Consider using SSH or personal access token.")

                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Git clone timed out after 60 seconds")
            return False
        except FileNotFoundError:
            print(f"   ❌ Git command not found. Please install Git:")
            print(f"      - Windows: https://git-scm.com/download/win")
            print(f"      - macOS: brew install git")
            print(f"      - Linux: sudo apt install git")
            return False
        except Exception as e:
            print(f"   ❌ Git clone error: {e}")
            return False

    def _verify_remote_url(self, local_path: Path, expected_url: str):
        """Verify that the remote URL is set correctly"""

        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                actual_url = result.stdout.strip()
                print(f"   🔗 Remote URL configured: {actual_url}")

                # Ensure SSH URL format if we expect SSH
                if expected_url.startswith('git@') and not actual_url.startswith('git@'):
                    print(f"   🔧 Updating remote URL to SSH format...")
                    subprocess.run(
                        ['git', 'remote', 'set-url', 'origin', expected_url],
                        cwd=local_path,
                        timeout=5
                    )
                    print(f"   ✅ Remote URL updated to: {expected_url}")

        except Exception as e:
            print(f"   ⚠️ Could not verify remote URL: {e}")

    def _analyze_local_repository(self, repo_url: str, owner: str,
                                  repo_name: str, local_path: Path) -> Dict:
        """Analyze cloned repository from filesystem"""

        print(f"   🔍 Analyzing local repository files...")

        # Get repository metadata
        repo_metadata = self._get_repo_metadata(local_path)

        # Find and read key configuration files
        key_files = self._read_key_files(local_path)

        # Analyze project structure
        project_structure = self._analyze_project_structure(local_path)

        # Detect technology stack
        tech_analysis = self._analyze_tech_stack(key_files, project_structure)

        analysis = {
            'repo_url': repo_url,
            'owner': owner,
            'repo_name': repo_name,
            'local_path': str(local_path),
            'description': repo_metadata.get('description', ''),
            'language': tech_analysis.get('primary_language', 'Unknown'),
            'default_branch': repo_metadata.get('default_branch', 'main'),
            'key_files': key_files,
            'project_structure': project_structure,
            'tech_stack': tech_analysis['tech_stack'],
            'build_tools': tech_analysis['build_tools'],
            'test_frameworks': tech_analysis['test_frameworks'],
            'ssh_configured': self.ssh_available,  # Add SSH status to analysis
            'summary': self._create_summary(tech_analysis, key_files,
                                            project_structure, repo_metadata)
        }

        print(f"   ✅ Analysis complete!")
        print(f"      🔤 Primary Language: {analysis['language']}")
        print(
            f"      🏗️ Tech Stack: {', '.join(tech_analysis['tech_stack']) if tech_analysis['tech_stack'] else 'None detected'}")
        print(
            f"      🔧 Build Tools: {', '.join(tech_analysis['build_tools']) if tech_analysis['build_tools'] else 'None detected'}")
        print(f"      📁 Key Files: {len(key_files)} found")
        print(f"      🔐 SSH Status: {'✅ Configured' if self.ssh_available else '❌ Not configured'}")

        return analysis

    def _get_repo_metadata(self, local_path: Path) -> Dict:
        """Extract repository metadata"""
        metadata = {}

        # Try to get description from README
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        for readme in readme_files:
            readme_path = local_path / readme
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')[
                              :500]  # First 500 chars
                    # Extract first non-empty line as description
                    lines = [line.strip() for line in content.split('\n') if
                             line.strip()]
                    if lines:
                        # Skip title lines that start with #
                        description_lines = [line for line in lines if
                                             not line.startswith('#')]
                        if description_lines:
                            metadata['description'] = description_lines[0]
                        else:
                            metadata['description'] = lines[0].replace('#',
                                                                       '').strip()
                    break
                except Exception:
                    continue

        # Try to get default branch from git
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                metadata['default_branch'] = result.stdout.strip() or 'main'
            else:
                metadata['default_branch'] = 'main'
        except Exception:
            metadata['default_branch'] = 'main'

        return metadata

    def _read_key_files(self, local_path: Path) -> Dict:
        """Read key configuration files from local repository"""

        print(f"      📄 Reading configuration files...")
        key_files = {}

        # Configuration files to look for
        config_files = [
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle',
            'Cargo.toml', 'Cargo.lock',
            'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile',
            'go.mod', 'go.sum',
            'pubspec.yaml', 'pubspec.lock',
            'composer.json', 'composer.lock',
            'Gemfile', 'Gemfile.lock',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'Makefile', 'CMakeLists.txt',
            '.gitignore', '.dockerignore',
            'tsconfig.json', 'webpack.config.js', 'vite.config.js',
            'jest.config.js', 'cypress.json', 'pytest.ini'
        ]

        for filename in config_files:
            file_path = local_path / filename
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    key_files[filename] = content[
                                          :3000]  # Limit content for AI processing
                    print(f"         ✅ {filename} ({len(content)} chars)")
                except Exception as e:
                    print(f"         ❌ Error reading {filename}: {e}")

        print(f"      📁 Found {len(key_files)} configuration files")
        return key_files

    def _analyze_project_structure(self, local_path: Path) -> Dict:
        """Analyze project directory structure"""

        structure = {
            'directories': [],
            'file_extensions': {},
            'total_files': 0,
            'source_files': 0
        }

        # Common source code extensions
        source_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.mjs',  # JavaScript/TypeScript
            '.py', '.pyx',  # Python
            '.java', '.kt', '.scala',  # JVM languages
            '.rs',  # Rust
            '.go',  # Go
            '.php',  # PHP
            '.rb',  # Ruby
            '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',  # C/C++
            '.cs',  # C#
            '.swift',  # Swift
            '.dart',  # Dart/Flutter
            '.vue',  # Vue
            '.html', '.htm', '.css', '.scss', '.sass', '.less',  # Web
            '.sql',  # SQL
            '.sh', '.bash', '.zsh',  # Shell scripts
        }

        try:
            for item in local_path.rglob('*'):
                # Skip hidden directories and common ignore patterns
                if any(part.startswith('.') for part in item.parts):
                    continue
                if any(ignore in str(item) for ignore in
                       ['node_modules', '__pycache__', 'target', 'build',
                        'dist']):
                    continue

                if item.is_file():
                    structure['total_files'] += 1

                    # Count file extensions
                    ext = item.suffix.lower()
                    structure['file_extensions'][ext] = structure[
                                                            'file_extensions'].get(
                        ext, 0) + 1

                    # Count source files
                    if ext in source_extensions:
                        structure['source_files'] += 1

                elif item.is_dir():
                    # Get relative path from repo root
                    rel_path = item.relative_to(local_path)
                    if len(rel_path.parts) <= 2:  # Only first 2 levels
                        structure['directories'].append(str(rel_path))

        except Exception as e:
            print(f"         ⚠️ Error analyzing structure: {e}")

        return structure

    def _analyze_tech_stack(self, key_files: Dict,
                            project_structure: Dict) -> Dict:
        """Analyze technology stack from files and structure"""

        tech_stack = []
        build_tools = []
        test_frameworks = []
        primary_language = "Unknown"

        # Analyze by configuration files
        if 'package.json' in key_files:
            tech_stack.append('Node.js')
            build_tools.append('npm')
            primary_language = "JavaScript"

            content = key_files['package.json'].lower()
            if 'react' in content:
                tech_stack.append('React')
            if 'vue' in content:
                tech_stack.append('Vue.js')
            if 'angular' in content:
                tech_stack.append('Angular')
            if 'next' in content:
                tech_stack.append('Next.js')
            if 'express' in content:
                tech_stack.append('Express')
            if 'jest' in content:
                test_frameworks.append('Jest')
            if 'cypress' in content:
                test_frameworks.append('Cypress')
            if 'typescript' in content:
                tech_stack.append('TypeScript')
                primary_language = "TypeScript"

        if 'yarn.lock' in key_files:
            build_tools.append('Yarn')

        if 'pom.xml' in key_files:
            tech_stack.append('Java')
            build_tools.append('Maven')
            primary_language = "Java"

            content = key_files['pom.xml'].lower()
            if 'spring' in content:
                tech_stack.append('Spring Boot')
            if 'junit' in content:
                test_frameworks.append('JUnit')

        if 'build.gradle' in key_files:
            if 'Java' not in tech_stack:
                tech_stack.append('Java')
                primary_language = "Java"
            build_tools.append('Gradle')

        if 'Cargo.toml' in key_files:
            tech_stack.append('Rust')
            build_tools.append('Cargo')
            primary_language = "Rust"

        if any(f in key_files for f in
               ['requirements.txt', 'pyproject.toml', 'setup.py']):
            tech_stack.append('Python')
            build_tools.append('pip')
            primary_language = "Python"

            if 'pyproject.toml' in key_files:
                content = key_files['pyproject.toml'].lower()
                if 'django' in content:
                    tech_stack.append('Django')
                if 'flask' in content:
                    tech_stack.append('Flask')
                if 'fastapi' in content:
                    tech_stack.append('FastAPI')
                if 'pytest' in content:
                    test_frameworks.append('pytest')

        if 'go.mod' in key_files:
            tech_stack.append('Go')
            build_tools.append('Go modules')
            primary_language = "Go"

        if 'pubspec.yaml' in key_files:
            tech_stack.append('Flutter')
            build_tools.append('Flutter')
            primary_language = "Dart"

        if 'composer.json' in key_files:
            tech_stack.append('PHP')
            build_tools.append('Composer')
            primary_language = "PHP"

        if any(f in key_files for f in ['Dockerfile', 'docker-compose.yml']):
            tech_stack.append('Docker')
            build_tools.append('Docker')

        # Analyze by file extensions if no config files found
        if not tech_stack and project_structure['file_extensions']:
            extensions = project_structure['file_extensions']

            if any(ext in extensions for ext in ['.js', '.jsx', '.ts', '.tsx']):
                tech_stack.append('JavaScript')
                primary_language = "JavaScript"
                if any(ext in extensions for ext in ['.ts', '.tsx']):
                    tech_stack.append('TypeScript')
                    primary_language = "TypeScript"

            if '.py' in extensions:
                tech_stack.append('Python')
                primary_language = "Python"

            if '.java' in extensions:
                tech_stack.append('Java')
                primary_language = "Java"

            if '.rs' in extensions:
                tech_stack.append('Rust')
                primary_language = "Rust"

            if '.go' in extensions:
                tech_stack.append('Go')
                primary_language = "Go"

        return {
            'tech_stack': tech_stack,
            'build_tools': build_tools,
            'test_frameworks': test_frameworks,
            'primary_language': primary_language
        }

    def _create_summary(self, tech_analysis: Dict, key_files: Dict,
                        project_structure: Dict, metadata: Dict) -> str:
        """Create comprehensive summary for AI"""

        return f"""Repository Analysis (Local Clone):
Primary Language: {tech_analysis['primary_language']}
Technology Stack: {', '.join(tech_analysis['tech_stack']) if tech_analysis['tech_stack'] else 'Unknown'}
Build Tools: {', '.join(tech_analysis['build_tools']) if tech_analysis['build_tools'] else 'None detected'}
Test Frameworks: {', '.join(tech_analysis['test_frameworks']) if tech_analysis['test_frameworks'] else 'None detected'}
Configuration Files: {', '.join(key_files.keys()) if key_files else 'None found'}
Total Files: {project_structure['total_files']}
Source Files: {project_structure['source_files']}
Main Directories: {', '.join(project_structure['directories'][:10]) if project_structure['directories'] else 'None'}
Description: {metadata.get('description', 'No description found')}
Default Branch: {metadata.get('default_branch', 'main')}
SSH Status: {'✅ Configured' if self.ssh_available else '❌ Not configured'}"""