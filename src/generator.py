"""
Improved AI-powered Jenkins File Generator
Enhanced prompt engineering for Claude 3.5 Haiku
"""

import json
import os
from pathlib import Path
from typing import Dict

from openrouter_client import OpenRouterClient


class JenkinsAIGenerator:
    """AI-powered Jenkins pipeline generator with enhanced prompts"""

    def __init__(self, model: str = None):
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
        """Generate all three Jenkins files with separate AI calls for better accuracy"""

        print(f"🤖 Generating Jenkins files with {self.model}...")

        files = {}

        # Generate each file separately for better accuracy
        try:
            print("   📄 Generating Jenkinsfile...")
            files['Jenkinsfile'] = self._generate_jenkinsfile(repo_analysis)

            print("   📄 Generating pipeline job config...")
            files['pipeline_job_config.xml'] = self._generate_job_config(repo_analysis)

            print("   📄 Generating plugin requirements...")
            files['required_plugins.xml'] = self._generate_plugins_xml(repo_analysis)

            print("   ✅ All files generated successfully")
            return files

        except Exception as e:
            print(f"   ❌ Error during generation: {e}")
            # Fallback to original method
            return self._generate_all_files_fallback(repo_analysis)

    def _generate_jenkinsfile(self, repo_analysis: Dict) -> str:
        """Generate Jenkinsfile with focused prompting"""

        system_prompt = """You are an expert DevOps engineer specializing in Jenkins declarative pipelines.

Generate a complete, production-ready Jenkinsfile using declarative pipeline syntax.

CRITICAL REQUIREMENTS:
- Use ONLY declarative pipeline syntax (pipeline { ... })
- Use default agent "any"
- Add comprehensive stages for the detected technology stack
- Include post-build actions (cleanup, notifications)
- Use environment variables and parameters appropriately
- Add proper error handling and timeout configurations
- Make it immediately runnable in Jenkins
- Review multiple times for accuracy

RESPONSE FORMAT:
Return ONLY the Jenkinsfile content, no explanations or markdown.
Start with: pipeline {
End with: }"""

        prompt = self._create_jenkinsfile_prompt(repo_analysis)

        response = self.client.generate(prompt, system_prompt)
        return self._clean_jenkinsfile_response(response)

    def _generate_job_config(self, repo_analysis: Dict) -> str:
        """Generate pipeline job config with enhanced XML prompting"""

        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are an expert Jenkins administrator. Generate a complete pipeline job configuration XML.

{jenkins_context_info}

CRITICAL XML STRUCTURE REQUIREMENTS:

1. ROOT ELEMENT:
<flow-definition plugin="workflow-job">

2. PROPERTIES SECTION - Use EXACT structure:
<properties>
  <hudson.model.ParametersDefinitionProperty>
    <parameterDefinitions>
      <hudson.model.StringParameterDefinition>
        <name>BRANCH_NAME</name>
        <description>Branch to build</description>
        <defaultValue>main</defaultValue>
        <trim>true</trim>
      </hudson.model.StringParameterDefinition>
    </parameterDefinitions>
  </hudson.model.ParametersDefinitionProperty>
  <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
    <triggers>
      <com.cloudbees.jenkins.GitHubPushTrigger plugin="github">
        <spec></spec>
      </com.cloudbees.jenkins.GitHubPushTrigger>
    </triggers>
  </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
</properties>

3. DEFINITION SECTION:
<definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
  <scm class="hudson.plugins.git.GitSCM" plugin="git">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>[REPO_URL]</url>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/${{BRANCH_NAME}}</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <submoduleCfg class="empty-list"/>
    <extensions/>
  </scm>
  <scriptPath>Jenkinsfile</scriptPath>
  <lightweight>true</lightweight>
</definition>

4. STANDARD SECTIONS:
- <actions/>
- <description>[PROJECT_DESCRIPTION]</description>
- <keepDependencies>false</keepDependencies>
- <disabled>false</disabled>

RESPONSE FORMAT:
Return ONLY the complete XML content, no explanations.
Start with: <?xml version='1.1' encoding='UTF-8'?>
Use the exact structure above with proper substitutions."""

        prompt = self._create_job_config_prompt(repo_analysis)

        response = self.client.generate(prompt, system_prompt)
        return self._clean_xml_response(response)

    def _generate_plugins_xml(self, repo_analysis: Dict) -> str:
        """Generate plugins XML with focused prompting"""

        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are a Jenkins plugin expert. Generate an XML file listing ONLY the plugins needed for this pipeline that are NOT already installed.

{jenkins_context_info}

CRITICAL REQUIREMENTS:
- ONLY include plugins that are NOT in the installed plugins list above
- Use standard plugin versions compatible with the Jenkins version
- Use this EXACT XML structure:

<?xml version="1.0" encoding="UTF-8"?>
<plugins>
  <plugin>plugin-name@version</plugin>
  <plugin>another-plugin@version</plugin>
</plugins>

COMMON PLUGINS NEEDED (only if not installed):
- workflow-aggregator (for pipeline support)
- git (for Git SCM)
- github (for GitHub integration)
- docker-workflow (for Docker)
- nodejs (for Node.js)
- maven-plugin (for Maven)
- gradle (for Gradle)
- junit (for test results)
- slack (for notifications)

RESPONSE FORMAT:
Return ONLY the XML content, no explanations."""

        prompt = self._create_plugins_prompt(repo_analysis)

        response = self.client.generate(prompt, system_prompt)
        return self._clean_xml_response(response)

    def _create_jenkinsfile_prompt(self, repo_analysis: Dict) -> str:
        """Create focused prompt for Jenkinsfile generation"""

        tech_stack = repo_analysis.get('tech_stack', [])
        build_tools = repo_analysis.get('build_tools', [])

        return f"""Generate a Jenkins declarative pipeline for this repository:

REPOSITORY DETAILS:
- URL: {repo_analysis['repo_url']}
- Language: {repo_analysis['language']}
- Tech Stack: {', '.join(tech_stack)}
- Build Tools: {', '.join(build_tools)}
- Default Branch: {repo_analysis['default_branch']}

KEY CONFIGURATION FILES:
{self._format_key_files(repo_analysis['key_files'])}

PIPELINE REQUIREMENTS:
1. Use appropriate agent (docker/node/maven based on tech stack)
2. Include stages: Checkout, Build, Test, Analysis, Deploy
3. Add environment variables for common settings
4. Include post-build cleanup and notifications
5. Add timeout configurations
6. Handle different branches appropriately

Make it production-ready and immediately runnable."""

    def _create_job_config_prompt(self, repo_analysis: Dict) -> str:
        """Create focused prompt for job config generation"""

        return f"""Generate Jenkins pipeline job configuration XML for:

REPOSITORY: {repo_analysis['repo_url']}
DESCRIPTION: {repo_analysis.get('description', 'AI-generated Jenkins pipeline')}
BRANCH: {repo_analysis['default_branch']}

REQUIREMENTS:
1. Configure GitHub integration with webhook trigger
2. Add BRANCH_NAME parameter (default: {repo_analysis['default_branch']})
3. Set up Git SCM with proper branch specifications
4. Enable lightweight checkout for performance
5. Set Jenkinsfile as the pipeline script path

Use the exact XML structure provided in the system prompt."""

    def _create_plugins_prompt(self, repo_analysis: Dict) -> str:
        """Create focused prompt for plugins generation"""

        tech_stack = repo_analysis.get('tech_stack', [])
        build_tools = repo_analysis.get('build_tools', [])

        return f"""Analyze the required plugins for this technology stack:

TECH STACK: {', '.join(tech_stack)}
BUILD TOOLS: {', '.join(build_tools)}
LANGUAGE: {repo_analysis['language']}

Generate XML listing ONLY the missing plugins needed for:
1. Basic pipeline functionality
2. Git/GitHub integration  
3. Build tool support ({', '.join(build_tools)})
4. Testing and reporting
5. Docker support (if Dockerfile detected)

Remember: Only include plugins NOT already installed in Jenkins."""

    def _format_key_files(self, key_files: Dict) -> str:
        """Format key files for prompt"""
        if not key_files:
            return "No configuration files found"

        formatted = []
        for filename, content in list(key_files.items())[:5]:  # Limit to 5 files
            formatted.append(f"{filename}: {content[:300]}...")

        return "\n".join(formatted)

    def _clean_jenkinsfile_response(self, response: str) -> str:
        """Clean and validate Jenkinsfile response"""
        # Remove markdown code blocks if present
        if "```" in response:
            parts = response.split("```")
            for part in parts:
                if "pipeline {" in part:
                    response = part.strip()
                    break

        # Ensure it starts with pipeline {
        if not response.strip().startswith("pipeline {"):
            # Try to extract pipeline block
            start = response.find("pipeline {")
            if start != -1:
                response = response[start:]

        return response.strip()

    def _clean_xml_response(self, response: str) -> str:
        """Clean and validate XML response"""
        # Remove markdown code blocks if present
        if "```" in response:
            parts = response.split("```")
            for part in parts:
                if "<?xml" in part or "<" in part:
                    response = part.strip()
                    break

        # Ensure it starts with XML declaration or root element
        response = response.strip()
        if not response.startswith("<?xml") and not response.startswith("<"):
            # Try to find XML content
            start = max(response.find("<?xml"), response.find("<"))
            if start != -1:
                response = response[start:]

        return response.strip()

    def _generate_all_files_fallback(self, repo_analysis: Dict) -> Dict[str, str]:
        """Fallback to original method if separate generation fails"""
        print("   🔄 Using fallback generation method...")

        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are an expert DevOps engineer specializing in Jenkins pipeline creation.

Generate THREE complete files for Jenkins pipeline setup:
1. Jenkinsfile (declarative pipeline)
2. pipeline_job_config.xml (Jenkins job configuration)
3. required_plugins.xml (plugin installation list)

JENKINS CONTEXT:
{jenkins_context_info}

RESPONSE FORMAT:
Structure your response exactly like this:

=== JENKINSFILE ===
[Complete Jenkinsfile content here]

=== PIPELINE_JOB_CONFIG ===
[Complete pipeline_job_config.xml content here]

=== REQUIRED_PLUGINS ===
[Complete required_plugins.xml content here]

=== END ==="""

        prompt = f"""Generate complete Jenkins pipeline files for this repository:

{repo_analysis['summary']}

Repository Details:
- URL: {repo_analysis['repo_url']}
- Description: {repo_analysis['description']}
- Default Branch: {repo_analysis['default_branch']}

Key Configuration Files:
{self._format_key_files(repo_analysis['key_files'])}

Generate all three files with production-ready configurations."""

        response = self.client.generate(prompt, system_prompt)
        return self._parse_structured_response(response)

    def modify_files(self, current_files: Dict[str, str], user_feedback: str, repo_analysis: Dict) -> Dict[str, str]:
        """Modify existing files based on user feedback using enhanced prompting"""

        jenkins_context_info = self._create_jenkins_context_info()

        system_prompt = f"""You are an expert DevOps engineer. Modify existing Jenkins files based on user feedback.

{jenkins_context_info}

RESPONSE FORMAT:
Structure your response exactly like this:

=== JENKINSFILE ===
[Modified Jenkinsfile content here]

=== PIPELINE_JOB_CONFIG ===
[Modified pipeline_job_config.xml content here]

=== REQUIRED_PLUGINS ===
[Modified required_plugins.xml content here]

=== END ===

Maintain the same quality and structure as the original files."""

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

        installed_plugins = self.jenkins_context.get('installed_plugins', {})
        categories = self.jenkins_context.get('plugin_categories', {})

        for category, plugins in categories.items():
            if plugins:
                context_info += f"\n{category.title()}: "
                plugin_list = []
                for plugin in plugins[:10]:
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