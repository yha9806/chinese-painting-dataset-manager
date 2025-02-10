from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chinese-painting-dataset-manager",
    version="2.0.0",
    author="yha9806",
    author_email="yha9806@example.com",
    description="中国画数据集管理系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yha9806/chinese-painting-dataset-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "chinese-painting-manager=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.html", "*.css", "*.js"],
    },
) 