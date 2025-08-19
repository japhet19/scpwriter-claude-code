from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scp-writer",
    version="0.1.0",
    author="Japhet",
    description="Multi-agent AI system for collaborative SCP story creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scpwriter",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "frontend", "api"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "api": [
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.32.0",
            "websockets>=14.1",
            "python-multipart>=0.0.9",
            "anyio>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "scp-writer=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["prompts/*.txt", "*.md", "LICENSE"],
    },
    zip_safe=False,
)