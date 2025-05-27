"""
AI-powered Jenkins File Generator
Generates Jenkinsfile, pipeline config, and plugin requirements using AI
"""

import json
from pathlib import Path
from typing import Dict

from openrouter_client import OpenRouterClient


class JenkinsAIGenerator:
    """AI-powered Jenkins pipeline generator"""

    def __init__(self, model: str = None):
        # Use provided model or get from environment
        ai_model = model or os.getenv('AI_MODEL', 'anthropic/claude-3-haiku')
        self.client = OpenRouterClient(model=ai_model)
        self.model = ai_model
        self.jenkins_context = self._load_jenkins_context()

    def _load_jenkins_context(self) -> Dict:
        """Load Jenkins context if available"""
        try:
            context_file = Path("./output/jenkins_context.json")
            if context_file.exists():
                with open(context_file, 'r') as f:
                    context = json.load(f)
                print(f"   ✅ Loaded Jenkins context: {len(context.get('installed_plugins', {}))} plugins detected")
                return context
        except Exception as e:
            print(f"   ⚠️ Could not load Jenkins context: {e}")

        return {"jenkins_accessible": False, "installed_plugins": {}, "version_info": {}}

    def generate_all_files(self, repo_analysis: Dict) -> Dict[str, str]:
        """Generate all three Jenkins files in one structured response"""

        # Create Jenkins context information for AI
        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are an expert DevOps engineer specializing in Jenkins pipeline creation.

Generate THREE complete files for Jenkins pipeline setup:
1. Jenkinsfile (declarative pipeline)
2. pipeline_job_config.xml (Jenkins job configuration)
3. required_plugins.xml (plugin installation list)

JENKINS CONTEXT:
{jenkins_context_info}

CRITICAL XML STRUCTURE REQUIREMENTS for pipeline_job_config.xml:
- Use ONLY standard Jenkins XML structure
- Parameters MUST be wrapped in ParametersDefinitionProperty:
  <hudson.model.ParametersDefinitionProperty>
    <parameterDefinitions>
      <hudson.model.StringParameterDefinition>
        <n>PARAM_NAME</n>
        <description>Description</description>
        <defaultValue>default</defaultValue>
      </hudson.model.StringParameterDefinition>
    </parameterDefinitions>
  </hudson.model.ParametersDefinitionProperty>
- Do NOT use CredentialsParameterDefinition in XML - use string parameters instead
- Use standard plugin versions without specific build numbers
- Keep XML structure simple and compatible

CRITICAL REQUIREMENTS:
- Generate COMPLETE, production-ready files with no placeholders
- Use proper syntax and formatting for each file type
- Make files immediately usable in Jenkins
- Include all necessary configurations and dependencies
- Add proper error handling and cleanup
- For required_plugins.xml: ONLY include plugins that are NOT already installed
- Use correct plugin versions compatible with the Jenkins version

RESPONSE FORMAT:
Structure your response exactly like this:

=== JENKINSFILE ===
[Complete Jenkinsfile content here]

=== PIPELINE_JOB_CONFIG ===
[Complete pipeline_job_config.xml content here]

=== REQUIRED_PLUGINS ===
[Complete required_plugins.xml content here - ONLY new plugins needed]

=== END ==="""

        prompt = f"""Generate complete Jenkins pipeline files for this repository:

{repo_analysis['summary']}

Repository Details:
- URL: {repo_analysis['repo_url']}
- Description: {repo_analysis['description']}
- Default Branch: {repo_analysis['default_branch']}
- Local Analysis: Repository was cloned and analyzed from filesystem

Key Configuration Files Found:
{chr(10).join([f"{name} ({len(content)} chars):\n{content[:800]}..." for name, content in repo_analysis['key_files'].items()])}

Project Structure:
- Total Files: {repo_analysis['project_structure']['total_files']}
- Source Files: {repo_analysis['project_structure']['source_files']}
- Main Directories: {', '.join(repo_analysis['project_structure']['directories'][:5])}

Generate all three files:

1. **Jenkinsfile**: Declarative pipeline with appropriate stages for this tech stack
2. **pipeline_job_config.xml**: Complete Jenkins job configuration for GitHub integration
3. **required_plugins.xml**: List of plugins needed for this pipeline to work

Make all files production-ready and immediately usable."""

        print(f"🤖 Generating all Jenkins files with {self.model}...")
        response = self.client.generate(prompt, system_prompt)

        return self._parse_structured_response(response)

    def modify_files(self, current_files: Dict[str, str], user_feedback: str, repo_analysis: Dict) -> Dict[str, str]:
        """Modify existing files based on user feedback"""

        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are an expert DevOps engineer. Modify existing Jenkins files based on user feedback.

JENKINS CONTEXT:
{jenkins_context_info}

Analyze the user's feedback and update the files accordingly. Maintain the same quality and structure.

RESPONSE FORMAT:
Structure your response exactly like this:

=== JENKINSFILE ===
[Modified Jenkinsfile content here]

=== PIPELINE_JOB_CONFIG ===
[Modified pipeline_job_config.xml content here]

=== REQUIRED_PLUGINS ===
[Modified required_plugins.xml content here]

=== END ==="""

        prompt = f"""User feedback: {user_feedback}

Current files to modify:

**Current Jenkinsfile:**
{current_files.get('Jenkinsfile', 'Not found')}

**Current pipeline_job_config.xml:**
{current_files.get('pipeline_job_config.xml', 'Not found')}

**Current required_plugins.xml:**
{current_files.get('required_plugins.xml', 'Not found')}

Repository context: {repo_analysis['summary']}

Please modify the files based on the user's feedback. Keep all files complete and production-ready."""

        print(f"🔄 Modifying files based on feedback...")
        response = self.client.generate(prompt, system_prompt)

        return self._parse_structured_response(response)

    def _create_jenkins_context_info(self) -> str:
        """Create Jenkins context information for AI prompt"""
        if not self.jenkins_context.get('jenkins_accessible'):
            return """Jenkins Context: Not accessible - generate standard plugin list
Note: Include common plugin versions and standard dependencies"""

        context_info = f"""Jenkins Context: 
Jenkins Version: {self.jenkins_context.get('version_info', {}).get('jenkins_version', 'Unknown')}
System Info: {self.jenkins_context.get('version_info', {}).get('system_info', 'Unknown')}

ALREADY INSTALLED PLUGINS ({len(self.jenkins_context.get('installed_plugins', {}))} total):"""

        # Group installed plugins by category
        installed_plugins = self.jenkins_context.get('installed_plugins', {})
        categories = self.jenkins_context.get('plugin_categories', {})

        for category, plugins in categories.items():
            if plugins:
                context_info += f"\n{category.title()}: "
                plugin_list = []
                for plugin in plugins[:10]:  # Limit to first 10 per category
                    version = installed_plugins.get(plugin, 'unknown')
                    plugin_list.append(f"{plugin}({version})")
                context_info += ", ".join(plugin_list)
                if len(plugins) > 10:
                    context_info += f" ... and {len(plugins) - 10} more"

        context_info += f"""

IMPORTANT: Do NOT include any of the above plugins in required_plugins.xml
Only suggest NEW plugins that are actually needed for the pipeline but not already installed.
Use appropriate versions compatible with Jenkins {self.jenkins_context.get('version_info', {}).get('jenkins_version', 'LTS')}"""

        return context_info

    def _parse_structured_response(self, response: str) -> Dict[str, str]:
        """Parse the structured AI response into separate files"""

        files = {}
        current_section = None
        current_content = []

        lines = response.split('\n')

        for line in lines:
            if line.strip() == "=== JENKINSFILE ===":
                current_section = "Jenkinsfile"
                current_content = []
            elif line.strip() == "=== PIPELINE_JOB_CONFIG ===":
                if current_section and current_content:
                    files[current_section] = '\n'.join(current_content).strip()
                current_section = "pipeline_job_config.xml"
                current_content = []
            elif line.strip() == "=== REQUIRED_PLUGINS ===":
                if current_section and current_content:
                    files[current_section] = '\n'.join(current_content).strip()
                current_section = "required_plugins.xml"
                current_content = []
            elif line.strip() == "=== END ===":
                if current_section and current_content:
                    files[current_section] = '\n'.join(current_content).strip()
                break
            elif current_section:
                current_content.append(line)

        # Handle case where END marker is missing
        if current_section and current_content and current_section not in files:
            files[current_section] = '\n'.join(current_content).strip()

        return files