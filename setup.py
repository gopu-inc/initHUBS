from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="inithub-cli",
    version="1.0.0",
    author="gopu-inc",
    author_email="ceoseshell@gmail.com",
    description="CLI officiel pour la plateforme initHUB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gopu-inc/iniHUBS",
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "inithub=inithub.cli:main",
        ],
    },
    include_package_data=True,
)
