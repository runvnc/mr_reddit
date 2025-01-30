from setuptools import setup, find_packages

setup(
    name="mr_reddit",
    version="1.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "praw>=7.7.0",
        "asyncpraw>=7.7.0",
        "python-dotenv>=0.19.0"
    ],
    author="MindRoot",
    author_email="info@mindroot.ai",
    description="Reddit bot plugin for MindRoot",
    keywords="reddit,bot,ai,mindroot",
    python_requires=">=3.9"
)
