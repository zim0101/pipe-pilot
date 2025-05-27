"""
Jenkins AI Agent
Main orchestrator for Jenkins pipeline generation
"""

import json
import os
from pathlib import Path
from typing import Dict

from analyzer import LocalRepositoryAnalyzer
from generator import JenkinsAIGenerator
from automation import JenkinsAutomation
from jenkins_cli import JenkinsCLIHelper


class JenkinsAIAgent:
    """Main Jenkins AI Agent with local git cloning and automation"""

    def __init__(self, model: str = None, repos_dir: str = "./repos"):
        # Use provided model or get from environment
        ai_model = model or os.getenv('AI_MODEL', 'anthropic/claude-3-haiku')
        self.analyzer = LocalRepositoryAnalyzer(repos_dir)
        self.generator = JenkinsAIGenerator(ai_model)
        self.model = ai_model
        self.current_files = {}
        self.repo_analysis = {}
        self.output_dir = Path("./output")
        self.jenkins_cli_helper = None

    def initialize_project(self, repo_url: str, output_dir: str = "./output") -> bool:
        """Initialize new project with local git clone and analysis"""

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        print(f"🚀 Jenkins AI Agent - Local Git Clone Mode")
        print(f"📂 Output directory: {self.output_dir.absolute()}")
        print(f"🤖 AI Model: {self.model}")

        # Always setup Jenkins context automatically
        print(f"\n🔧 Setting up Jenkins CLI and context...")
        jenkins_cli_success = self._setup_jenkins_context()
        if jenkins_cli_success:
            print(f"   ✅ Jenkins context created successfully")
            # Reload context in generator
            self.generator.jenkins_context = self.generator._load_jenkins_context()
        else:
            print(f"   ⚠️ Jenkins detection failed, continuing without context")

        try:
            # Step 1: Clone and analyze repository
            print(f"\n📊 Cloning and analyzing repository...")
            self.repo_analysis = self.analyzer.clone_and_analyze(repo_url)

            # Step 2: Generate all files
            print(f"\n🤖 Generating Jenkins files...")
            self.current_files = self.generator.generate_all_files(self.repo_analysis)

            # Step 3: Save files
            self._save_files()

            # Step 4: Save analysis
            analysis_path = self.output_dir / "repository_analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(self.repo_analysis, f, indent=2)

            print(f"\n✅ Project initialized successfully!")
            self._show_file_summary()

            return True

        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            return False

    def modify_project(self, user_feedback: str) -> bool:
        """Modify existing project files based on user feedback"""

        if not self.current_files or not self.repo_analysis:
            print("❌ No project initialized. Run initialize_project() first.")
            return False

        try:
            print(f"\n🔄 Processing feedback: {user_feedback}")

            # Generate modified files
            self.current_files = self.generator.modify_files(
                self.current_files,
                user_feedback,
                self.repo_analysis
            )

            # Save updated files
            self._save_files()

            print(f"\n✅ Files updated successfully!")
            self._show_file_summary()

            return True

        except Exception as e:
            print(f"❌ Error during modification: {e}")
            return False

    def start_automation(self) -> bool:
        """Start the automation phase - git push, job creation, plugin installation"""

        if not self.current_files or not self.repo_analysis:
            print("❌ No project initialized. Cannot start automation.")
            return False

        try:
            # Create automation instance
            automation = JenkinsAutomation(
                repo_analysis=self.repo_analysis,
                output_dir=str(self.output_dir),
                jenkins_cli_helper=self.jenkins_cli_helper
            )

            # Start the automation flow
            return automation.start_automation_flow()

        except Exception as e:
            print(f"❌ Error during automation: {e}")
            return False

    def _setup_jenkins_context(self) -> bool:
        """Set up Jenkins context automatically using .env credentials"""
        try:
            # Import the Jenkins CLI helper
            from jenkins_cli import create_jenkins_context_file

            # Use environment variables (no user input needed)
            print(f"      📡 Using Jenkins credentials from .env file")
            print(f"      🔧 Jenkins URL: {os.getenv('JENKINS_URL', 'http://localhost:8080')}")
            print(f"      👤 Username: {os.getenv('JENKINS_USERNAME', 'admin')}")

            # Create Jenkins CLI helper instance for automation
            self.jenkins_cli_helper = JenkinsCLIHelper()

            # Create Jenkins context using environment variables
            success = create_jenkins_context_file(str(self.output_dir))

            return success

        except Exception as e:
            print(f"      ❌ Error setting up Jenkins context: {e}")
            return False

    def _save_files(self):
        """Save all generated files to output directory"""

        for filename, content in self.current_files.items():
            file_path = self.output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

    def _show_file_summary(self):
        """Show summary of generated files"""

        print(f"\n📁 Generated files in {self.output_dir}:")

        for filename in self.current_files.keys():
            file_path = self.output_dir / filename
            file_size = file_path.stat().st_size
            print(f"   📄 {filename} ({file_size} bytes)")

        print(f"   📊 repository_analysis.json")

        print(f"\n🎯 Next steps:")
        print(f"   1. Review the generated files")
        print(f"   2. Type 'ready' to start automation:")
        print(f"      • Commit and push Jenkinsfile to repository")
        print(f"      • Create Jenkins pipeline job")
        print(f"      • Install required plugins")
        print(f"   3. Or provide feedback to improve the pipeline")