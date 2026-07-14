# -*- coding: utf-8 -*-
"""MoLock SDK setup."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="molock",
    version="1.0.0",
    author="孙巍珑",
    author_email="3042652889@qq.com",
    description="墨锁（MoLock）：基于墨家经说双链的大语言模型中文语义约束推理框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llxpy/-MoLock",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
        ],
    },
    keywords="chinese NLP LLM hallucination semantic-constraint mohist-logic anti-hallucination",
    project_urls={
        "Source": "https://github.com/llxpy/-MoLock",
        "Paper": "https://github.com/llxpy/-MoLock/tree/main/paper",
    },
)
