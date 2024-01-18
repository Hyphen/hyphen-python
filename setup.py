from pathlib import Path
from setuptools import setup, find_packages

docs = Path(__file__).parent / "docs"
#long_description_file = docs / "pypi" / "long_description.md"
#assert long_description_file.exists(), "no long description file!"
#long_description = long_description_file.read_text()
#version = Path(__file__).parent / "version.txt"
#assert version.exists(), "no version!"
#version.read_text().strip()

long_description = "Official Python SDK for the Hyphen API"
version = "0.0.1a0"
setup(
    name="hyphen",
    version=version,
    description="Official Python SDK for the Hyphen API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hyphen.ai",
    author_email="support@hyphen.ai",
    url="https://github.com/hyphen/hyphen-python",
    license="MIT",
    keywords="hyphen api teams",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    zip_safe=False,
    install_requires=[
        'requests >= 2.20; python_version >= "3.0"',
    ],
    python_requires=">=3.6",
    project_urls={
        "Bug Tracker": "https://github.com/hyphen/hyphen-python/issues",
        "Changes": "https://github.com/hyphen/hyphen-python/blob/master/CHANGELOG.md",
        "Documentation": "https://docs.hyphen.com",
        "Source Code": "https://github.com/hyphen/hyphen-python",
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["wheel"],
)
