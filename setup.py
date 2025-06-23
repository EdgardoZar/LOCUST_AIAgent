"""
Setup script for Locust AI Agent
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Locust AI Agent - Automated performance testing with AI analysis"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="locust-ai-agent",
    version="1.0.0",
    author="AI Assistant",
    description="AI-powered solution for automating Locust performance testing in CI/CD pipelines",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Acceptance",
        "Topic :: Software Development :: Testing :: Load",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "locust-ai-agent=Locust_AI_Agent.utils.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="locust performance testing ai automation ci-cd jenkins",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/locust-ai-agent/issues",
        "Source": "https://github.com/your-repo/locust-ai-agent",
        "Documentation": "https://github.com/your-repo/locust-ai-agent/blob/main/README.md",
    },
) 