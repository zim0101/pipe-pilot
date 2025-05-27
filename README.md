# 🚀 Pipe Pilot

<div align="center">

```
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
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**The ultimate AI-powered DevOps automation tool that transforms any GitHub repository into a production-ready Jenkins CI/CD pipeline in minutes!**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Jenkins](https://img.shields.io/badge/Jenkins-2.400+-orange.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)

</div>

## ✨ What is Pipe Pilot?

Pipe Pilot is a revolutionary AI-powered tool that automatically generates complete Jenkins CI/CD pipelines by analyzing your repository structure, dependencies, and technology stack. No more manual pipeline configuration - just point it at your GitHub repo and watch the magic happen!

### 🎯 Key Features

- **🤖 AI-Powered Analysis**: Uses advanced AI models (Claude, GPT-4, Llama) to understand your codebase
- **🔍 Multi-Language Support**: JavaScript/TypeScript, Python, Java, Go, Rust, PHP, and more
- **🔐 Smart SSH Detection**: Automatically detects and uses your SSH configuration
- **🏗️ Complete Automation**: Git push + Jenkins job creation + plugin installation
- **📦 Plugin Intelligence**: Only installs missing plugins based on your Jenkins instance
- **🔄 Interactive Refinement**: Chat with AI to improve your pipeline
- **🎛️ Production Ready**: Generates immediately usable Jenkins configurations

### 🚀 How It Works

1. **Clone & Analyze** - Downloads and analyzes your repository locally
2. **AI Generation** - Creates Jenkinsfile, job config, and plugin requirements
3. **Interactive Chat** - Refine the pipeline with natural language feedback
4. **Automation** - Pushes code, creates Jenkins jobs, installs plugins
5. **Ready to Use** - Your CI/CD pipeline is live and running!

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** 
- **Git** configured with SSH keys
- **Jenkins 2.400+** running locally or remotely
- **OpenRouter API Key** ([Get free key](https://openrouter.ai/))

### Quick Install

```bash
# Clone the repository
git clone git@github.com:zim0101/pipe-pilot.git
cd pipe-pilot

# Create virtual environment and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
vim .env
or 
touch .env
```

### Configuration

Edit `.env` file with your settings:

```bash
# AI Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
AI_MODEL=anthropic/claude-3-haiku

# Jenkins Configuration  
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=admin
JENKINS_TOKEN=your_jenkins_api_token

# Optional
JENKINS_CLI_JAR=./jenkins-cli.jar
```

#### 🔑 Getting API Keys

1. **OpenRouter API Key**:
   - Visit [OpenRouter.ai](https://openrouter.ai/)
   - Sign up for free account
   - Generate API key from dashboard
   - Add to `.env` file

2. **Jenkins API Token**:
   - Go to Jenkins → User → Configure → API Token
   - Generate new token
   - Add to `.env` file

## 🚀 Usage

### Basic Usage

```bash
# Generate pipeline for any GitHub repository
python main.py https://github.com/username/repository

# Use specific AI model
python main.py https://github.com/username/repo anthropic/claude-3.5-sonnet
```

### Interactive Example

```bash
$ python main.py https://github.com/facebook/react

# 🎨 ASCII banner displays
# 🔍 Environment verification
# 📊 Repository analysis  
# 🤖 AI pipeline generation

💬 Interactive Mode - Provide feedback to improve the pipeline
📝 Your feedback (or 'exit'/'ready'): add docker build stage

# ✏️ AI modifies the pipeline

📝 Your feedback (or 'exit'/'ready'): ready

# 🚀 Full automation begins:
# ✅ Jenkinsfile committed and pushed
# ✅ Jenkins job created  
# ✅ Required plugins installed

🏁 Your Jenkins pipeline is ready to use!
```

### Command Options

| Command | Description |
|---------|-------------|
| `python main.py <repo_url>` | Generate pipeline for repository |
| `python main.py <repo_url> <model>` | Use specific AI model |
| `--help` | Show help information |

### Interactive Commands

| Command | Description |
|---------|-------------|
| `ready` | Start full automation (git + jenkins + plugins) |
| `help` | Show example feedback prompts |
| `exit`/`quit` | End session |
| Any text | Provide feedback to improve pipeline |

## 🎛️ Supported Technologies

### Languages & Frameworks
- **JavaScript/TypeScript**: React, Vue, Angular, Next.js, Express
- **Python**: Django, Flask, FastAPI
- **Java**: Spring Boot, Maven, Gradle  
- **Go**: Go modules
- **Rust**: Cargo
- **PHP**: Composer
- **And many more...**

### Build Tools
- npm, Yarn, pnpm
- Maven, Gradle
- Docker, Docker Compose
- pip, Poetry
- Cargo
- Go modules

### CI/CD Features
- Multi-stage pipelines
- Docker build & push
- Automated testing
- Code quality analysis
- Deployment automation
- Slack/email notifications

## 🔧 Advanced Configuration

### Custom AI Models

Pipe Pilot supports multiple AI providers:

```bash
# Claude models (recommended)
AI_MODEL=anthropic/claude-3-haiku          # Fast & cheap
AI_MODEL=anthropic/claude-3.5-sonnet       # Best quality

# OpenAI models  
AI_MODEL=openai/gpt-4o                     # High quality
AI_MODEL=openai/gpt-3.5-turbo             # Balanced

# Open source models
AI_MODEL=meta-llama/llama-3.1-8b-instruct:free  # Free tier
```

### Jenkins Configuration

```bash
# Local Jenkins
JENKINS_URL=http://localhost:8080

# Remote Jenkins  
JENKINS_URL=https://jenkins.yourcompany.com

# Custom port
JENKINS_URL=http://localhost:9090
```

### SSH Setup

Pipe Pilot automatically detects SSH configuration:

```bash
# Ensure SSH keys are loaded
ssh-add ~/.ssh/id_rsa

# Test GitHub connection
ssh -T git@github.com
```

## 📁 Generated Files

Pipe Pilot creates these files in the `output/` directory:

- **`Jenkinsfile`** - Complete declarative pipeline
- **`pipeline_job_config.xml`** - Jenkins job configuration
- **`required_plugins.xml`** - Missing plugins to install
- **`repository_analysis.json`** - Detailed code analysis
- **`jenkins_context.json`** - Jenkins environment info

## 🐛 Troubleshooting

### Common Issues

**API Key Not Working**
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY

# Check .env file
cat .env | grep OPENROUTER_API_KEY
```

**Jenkins Connection Failed**
```bash
# Test Jenkins connectivity
curl http://localhost:8080/api/json

# Check Jenkins CLI
java -jar jenkins-cli.jar -s http://localhost:8080 version
```

**SSH Authentication Issues**
```bash
# Check SSH agent
ssh-add -l

# Test GitHub connection
ssh -T git@github.com
```

**Git Push Failed**
```bash
# Verify SSH keys for GitHub
ssh -T git@github.com

# Check repository permissions
git remote -v
```

### Debug Mode

Enable verbose output:

```bash
DEBUG=true python main.py https://github.com/username/repo
```

## 🤝 Contributing

We love contributions! Here's how to help:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`  
5. **Open Pull Request**

### Development Setup

```bash
# Clone for development
git clone https://github.com/zim0101/ai-jenkins-pipeline-agent.git
cd ai-jenkins-pipeline-agent

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter** for providing access to multiple AI models
- **Jenkins** community for the amazing CI/CD platform
- **Anthropic** for Claude AI models
- **GitHub** for hosting and Git integration

## 🔗 Links

- [Documentation](https://github.com/zim0101/ai-jenkins-pipeline-agent/wiki)
- [Issue Tracker](https://github.com/zim0101/ai-jenkins-pipeline-agent/issues)
- [Discussions](https://github.com/zim0101/ai-jenkins-pipeline-agent/discussions)
- [OpenRouter API](https://openrouter.ai/)
- [Jenkins Documentation](https://jenkins.io/doc/)

---

<div align="center">

**Made with ❤️ by the Team Radioactive**

⭐ **Star this repo if Pipe Pilot helped you!** ⭐

</div>