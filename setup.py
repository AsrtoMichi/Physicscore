from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="Physicscore",
        version="0.2.0.0",
        author="AsrtoMichi",
        author_email="asrtomichi@gmail.com",
        maintainer="AsrtoMichi",
        maintainer_email="asrtomichi@gmail.com",
        url="https://github.com/AsrtoMichi/Physicscore",
        description="An app for physique competition in teams and analysis of it",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        download_url="https://github.com/AsrtoMichi/Physicscore/archive/refs/heads/main.zip",
        license="GPLv3",
        packages=find_packages(),
        py_modules=["matplotlib"],
        install_requires=[
            "matplotlib",
        ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Customer Service",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
        entry_points={
            "console_scripts": [
                "physicscore=Physicscore:main",
                "reportgenerator=ReportGenerator:main",
            ],
        },
        package_data={
            "": ["*.ico", "*.json"],
        },
        include_package_data=True,
        platforms=["Windows", "Linux", "Mac OS-X"]
    )
