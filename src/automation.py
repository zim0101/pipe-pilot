"""
Jenkins Automation Module
Handles automated deployment of Jenkinsfile, job creation, and plugin installation
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from jenkins_cli import JenkinsCLIHelper


class JenkinsAutomation:
    """Handles end-to-end Jenkins automation"""

    def __init__(self, repo_analysis: Dict, output_dir: str, jenkins_cli_helper: Optional[JenkinsCLIHelper] = None):
        self.repo_analysis = repo_analysis
        self.output_dir = Path(output_dir)
        self.local_repo_path = Path(repo_analysis['local_path'])
        self.jenkins_cli = jenkins_cli_helper or JenkinsCLIHelper()

    def start_automation_flow(self) -> bool:
        """Main automation flow with user interaction"""

        print(f"\n🚀 Jenkins Automation Phase")
        print(f"=" * 40)
        print(f"Ready to automate:")
        print(f"  📁 Repository: {self.repo_analysis['owner']}/{self.repo_analysis['repo_name']}")
        print(f"  📂 Local path: {self.local_repo_path}")
        print(f"  📄 Jenkinsfile: {self.output_dir}/Jenkinsfile")

        # Phase 1: Git Automation
        git_success = self.git_automation_phase()
        if not git_success:
            print(f"❌ Git automation failed or skipped")
            return False

        # Phase 2: Job Creation
        job_success = self.job_creation_phase()
        if not job_success:
            print(f"❌ Job creation failed or skipped")

        # Phase 3: Plugin Installation
        plugin_success = self.plugin_installation_phase()
        if not plugin_success:
            print(f"❌ Plugin installation failed or skipped")

        return git_success and job_success and plugin_success

    def git_automation_phase(self) -> bool:
        """Handle Jenkinsfile commit and push"""

        print(f"\n📦 Phase 1: Git Automation")
        print(f"-" * 30)

        # Check if Jenkinsfile exists in output
        jenkinsfile_source = self.output_dir / "Jenkinsfile"
        if not jenkinsfile_source.exists():
            print(f"❌ No Jenkinsfile found in {self.output_dir}")
            return False

        # Check current git status
        git_status = self._get_git_status()
        if not git_status['is_git_repo']:
            print(f"❌ Not a git repository: {self.local_repo_path}")
            return False

        print(f"📊 Repository Status:")
        print(f"   🔸 Current branch: {git_status['current_branch']}")
        print(f"   🔸 Jenkinsfile exists: {'✅' if git_status['has_jenkinsfile'] else '❌'}")
        print(f"   🔸 Uncommitted changes: {'✅' if git_status['has_changes'] else '❌'}")

        # Ask user for confirmation
        response = input(f"\n📝 Do you want to commit and push the Jenkinsfile? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print(f"⏭️ Skipping git automation")
            return False

        # Determine branching strategy
        if git_status['has_jenkinsfile']:
            target_branch = git_status['current_branch']
            print(f"🔄 Jenkinsfile exists, updating on current branch: {target_branch}")
        else:
            target_branch = "feature/jenkins-ci-cd-pipeline"
            print(f"✨ Creating new branch: {target_branch}")

        # Execute git operations
        return self._execute_git_operations(jenkinsfile_source, target_branch, git_status)

    def job_creation_phase(self) -> bool:
        """Handle Jenkins job creation"""

        print(f"\n🏗️ Phase 2: Jenkins Job Creation")
        print(f"-" * 35)

        # Check if pipeline config exists
        pipeline_config = self.output_dir / "pipeline_job_config.xml"
        if not pipeline_config.exists():
            print(f"❌ No pipeline config found: {pipeline_config}")
            return False

        # Get existing jobs
        existing_jobs = self._get_existing_jenkins_jobs()

        print(f"📋 Jenkins Job Status:")
        if existing_jobs:
            print(f"   🔸 Existing jobs ({len(existing_jobs)}):")
            for job in existing_jobs[:10]:  # Show first 10
                print(f"      • {job}")
            if len(existing_jobs) > 10:
                print(f"      ... and {len(existing_jobs) - 10} more")
        else:
            print(f"   🔸 No existing jobs found")

        # Ask for job name
        suggested_name = f"{self.repo_analysis['repo_name']}-pipeline"
        job_name = input(f"\n📝 Enter job name (or press Enter for '{suggested_name}'): ").strip()
        if not job_name:
            job_name = suggested_name

        if not job_name:
            print(f"⏭️ No job name provided, skipping job creation")
            return False

        # Warn if job exists
        if job_name in existing_jobs:
            response = input(f"⚠️ Job '{job_name}' already exists. Overwrite? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print(f"⏭️ Skipping job creation")
                return False

        # Create the job
        return self._create_jenkins_job(job_name, pipeline_config)

    def plugin_installation_phase(self) -> bool:
        """Handle plugin installation"""

        print(f"\n🔌 Phase 3: Plugin Installation")
        print(f"-" * 32)

        # Check if plugins file exists
        plugins_file = self.output_dir / "required_plugins.xml"
        if not plugins_file.exists():
            print(f"❌ No plugins file found: {plugins_file}")
            return False

        # Parse plugins from XML
        required_plugins = self._parse_plugins_xml(plugins_file)
        if not required_plugins:
            print(f"✅ No plugins need to be installed")
            return True

        print(f"📦 Plugins to install ({len(required_plugins)}):")
        for plugin in required_plugins:
            print(f"   • {plugin['name']} ({plugin['version']})")

        # Ask for confirmation
        response = input(f"\n📝 Install these plugins? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print(f"⏭️ Skipping plugin installation")
            return False

        # Install plugins
        return self._install_jenkins_plugins(required_plugins)

    def _get_git_status(self) -> Dict:
        """Get current git repository status"""

        status = {
            'is_git_repo': False,
            'current_branch': None,
            'has_jenkinsfile': False,
            'has_changes': False
        }

        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return status

            status['is_git_repo'] = True

            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                status['current_branch'] = result.stdout.strip() or 'main'

            # Check if Jenkinsfile exists
            jenkinsfile_path = self.local_repo_path / "Jenkinsfile"
            status['has_jenkinsfile'] = jenkinsfile_path.exists()

            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                status['has_changes'] = bool(result.stdout.strip())

        except Exception as e:
            print(f"⚠️ Error checking git status: {e}")

        return status

    def _execute_git_operations(self, jenkinsfile_source: Path, target_branch: str, git_status: Dict) -> bool:
        """Execute git add, commit, and push operations"""

        try:
            # Copy Jenkinsfile to repository
            jenkinsfile_dest = self.local_repo_path / "Jenkinsfile"
            print(f"📋 Copying Jenkinsfile...")
            shutil.copy2(jenkinsfile_source, jenkinsfile_dest)
            print(f"   ✅ Copied to: {jenkinsfile_dest}")

            # Create new branch if needed
            if target_branch != git_status['current_branch']:
                print(f"🌿 Creating new branch: {target_branch}")

                # Create and switch to new branch
                result = subprocess.run(
                    ['git', 'checkout', '-b', target_branch],
                    cwd=self.local_repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    print(f"❌ Failed to create branch: {result.stderr}")
                    return False

                print(f"   ✅ Created and switched to: {target_branch}")
            else:
                print(f"🔄 Using existing branch: {target_branch}")

            # Git add
            print(f"📦 Adding Jenkinsfile to git...")
            result = subprocess.run(
                ['git', 'add', 'Jenkinsfile'],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"❌ Failed to add Jenkinsfile: {result.stderr}")
                return False

            print(f"   ✅ Added Jenkinsfile")

            # Git commit
            commit_message = "Add Jenkins pipeline configuration"
            print(f"💾 Committing changes...")
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # Check if it's because there are no changes
                if "nothing to commit" in result.stdout:
                    print(f"   ℹ️ No changes to commit (Jenkinsfile already up to date)")
                else:
                    print(f"❌ Failed to commit: {result.stderr}")
                    return False
            else:
                print(f"   ✅ Committed: {commit_message}")

            # Git push
            print(f"🚀 Pushing to remote...")

            # For new branches, we need to set upstream and push
            if target_branch != git_status['current_branch']:
                # Push new branch with upstream tracking
                push_cmd = ['git', 'push', '--set-upstream', 'origin', target_branch]
                print(f"   📤 Setting upstream and pushing new branch...")
            else:
                # Push to existing branch
                push_cmd = ['git', 'push']
                print(f"   📤 Pushing to existing branch...")

            result = subprocess.run(
                push_cmd,
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"❌ Failed to push: {result.stderr}")
                print(f"💡 You may need to push manually:")
                print(f"   cd {self.local_repo_path}")
                print(f"   git push --set-upstream origin {target_branch}")
                return False

            print(f"   ✅ Pushed to origin/{target_branch}")
            print(f"🎉 Git automation completed successfully!")

            return True

        except subprocess.TimeoutExpired:
            print(f"⏰ Git operation timed out")
            return False
        except Exception as e:
            print(f"❌ Git operation failed: {e}")
            return False

    def _get_existing_jenkins_jobs(self) -> List[str]:
        """Get list of existing Jenkins jobs"""

        try:
            # Use Jenkins CLI to list jobs
            jobs_output = self.jenkins_cli._run_cli_command(['list-jobs'])
            if jobs_output:
                # Parse job names from output
                jobs = [line.strip() for line in jobs_output.split('\n') if line.strip()]
                return jobs
            else:
                print(f"⚠️ Could not retrieve Jenkins jobs")
                return []

        except Exception as e:
            print(f"⚠️ Error getting Jenkins jobs: {e}")
            return []

    def _create_jenkins_job(self, job_name: str, config_file: Path) -> bool:
        """Create Jenkins job from XML configuration"""

        try:
            print(f"🏗️ Creating Jenkins job: {job_name}")

            # Read the XML configuration
            config_content = config_file.read_text(encoding='utf-8')

            # Debug: Show XML size and first few lines
            print(f"   📄 XML config size: {len(config_content)} characters")
            lines = config_content.split('\n')[:5]
            print(f"   📝 First few lines: {lines}")

            # Create job using Jenkins CLI
            # Skip delete attempt since it's causing issues
            print(f"   🔧 Creating job directly...")

            # Create new job
            create_cmd = ['create-job', job_name]

            # Use echo to pipe XML content to Jenkins CLI
            try:
                cmd = [
                    'java', '-jar', self.jenkins_cli.cli_jar,
                    '-s', self.jenkins_cli.jenkins_url
                ]

                # Add authentication if available
                if self.jenkins_cli.username and self.jenkins_cli.token:
                    cmd.extend(['-auth', f'{self.jenkins_cli.username}:{self.jenkins_cli.token}'])

                cmd.extend(create_cmd)

                result = subprocess.run(
                    cmd,
                    input=config_content,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    print(f"   ✅ Job created successfully: {job_name}")
                    print(f"   🔗 Access at: {self.jenkins_cli.jenkins_url}/job/{job_name}/")
                    return True
                else:
                    print(f"   ❌ Failed to create job: {result.stderr}")
                    print(f"   📋 Stdout: {result.stdout}")

                    # Try creating a minimal pipeline job as fallback
                    print(f"   🔄 Trying fallback: minimal pipeline job...")
                    return self._create_minimal_pipeline_job(job_name)

            except subprocess.TimeoutExpired:
                print(f"   ⏰ Job creation timed out")
                return False

        except Exception as e:
            print(f"❌ Error creating Jenkins job: {e}")
            return False

    def _create_minimal_pipeline_job(self, job_name: str) -> bool:
        """Create a minimal pipeline job as fallback"""

        try:
            print(f"   🛠️ Creating minimal pipeline job...")

            # Minimal pipeline job XML
            minimal_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <actions/>
  <description>Jenkins pipeline for {self.repo_analysis.get('repo_name', job_name)}</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>-1</daysToKeep>
        <numToKeep>10</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.80">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.8.3">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{self.repo_analysis.get('repo_url', '')}</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""

            # Create job with minimal XML
            cmd = [
                'java', '-jar', self.jenkins_cli.cli_jar,
                '-s', self.jenkins_cli.jenkins_url
            ]

            if self.jenkins_cli.username and self.jenkins_cli.token:
                cmd.extend(['-auth', f'{self.jenkins_cli.username}:{self.jenkins_cli.token}'])

            cmd.extend(['create-job', job_name])

            result = subprocess.run(
                cmd,
                input=minimal_xml,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"   ✅ Minimal pipeline job created successfully!")
                print(f"   🔗 Access at: {self.jenkins_cli.jenkins_url}/job/{job_name}/")
                print(f"   📝 Note: Job created with basic configuration")
                print(f"   💡 You can customize it further in Jenkins UI")
                return True
            else:
                print(f"   ❌ Minimal job creation also failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Error creating minimal job: {e}")
            return False

    def _parse_plugins_xml(self, plugins_file: Path) -> List[Dict]:
        """Parse required plugins from XML file"""

        try:
            plugins_content = plugins_file.read_text(encoding='utf-8')
            plugins = []

            # Simple XML parsing for plugin entries
            # Look for patterns like: <plugin>name@version</plugin>
            import re

            # Pattern to match plugin entries
            plugin_pattern = r'<plugin[^>]*>([^<]+)</plugin>'
            matches = re.findall(plugin_pattern, plugins_content)

            for match in matches:
                # Parse name@version format
                if '@' in match:
                    name, version = match.split('@', 1)
                    plugins.append({'name': name.strip(), 'version': version.strip()})
                else:
                    plugins.append({'name': match.strip(), 'version': 'latest'})

            return plugins

        except Exception as e:
            print(f"⚠️ Error parsing plugins XML: {e}")
            return []

    def _install_jenkins_plugins(self, plugins: List[Dict]) -> bool:
        """Install Jenkins plugins using CLI"""

        try:
            print(f"🔌 Installing {len(plugins)} plugins...")

            success_count = 0

            for plugin in plugins:
                plugin_spec = f"{plugin['name']}"
                if plugin['version'] != 'latest':
                    plugin_spec += f":{plugin['version']}"

                print(f"   📦 Installing: {plugin_spec}")

                result = self.jenkins_cli._run_cli_command(['install-plugin', plugin_spec])

                if result is not None:
                    print(f"      ✅ Installed: {plugin['name']}")
                    success_count += 1
                else:
                    print(f"      ❌ Failed: {plugin['name']}")

            if success_count == len(plugins):
                print(f"🎉 All plugins installed successfully!")
                print(f"⚠️ Jenkins may need to be restarted for plugins to take effect")

                restart_response = input(f"🔄 Restart Jenkins now? (y/n): ").strip().lower()
                if restart_response in ['y', 'yes']:
                    self._restart_jenkins()

                return True
            elif success_count > 0:
                print(f"⚠️ Partial success: {success_count}/{len(plugins)} plugins installed")
                return True
            else:
                print(f"❌ No plugins were installed successfully")
                return False

        except Exception as e:
            print(f"❌ Error installing plugins: {e}")
            return False

    def _restart_jenkins(self) -> bool:
        """Restart Jenkins safely"""

        try:
            print(f"🔄 Restarting Jenkins safely...")

            result = self.jenkins_cli._run_cli_command(['safe-restart'])

            if result is not None:
                print(f"   ✅ Jenkins restart initiated")
                print(f"   ⏳ Jenkins will restart when current builds complete")
                return True
            else:
                print(f"   ❌ Failed to restart Jenkins")
                return False

        except Exception as e:
            print(f"❌ Error restarting Jenkins: {e}")
            return False