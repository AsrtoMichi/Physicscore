from setuptools import setup, find_packages
from os.path import join, dirname

if __name__ == "__main__":
    setup(
        name="Physicscore",
        version="0.2.1.0",
        author="AsrtoMichi",
        author_email="asrtomichi@gmail.com",
        maintainer="AsrtoMichi",
        maintainer_email="asrtomichi@gmail.com",
        url="https://github.com/AsrtoMichi/Physicscore",
        description="An app for physics competitions in teams and their analysis",
        long_description=open(join(dirname(__file__), "README.md"), encoding="utf-8").read(),
        long_description_content_type="text/markdown",
        download_url="https://github.com/AsrtoMichi/Physicscore/archive/refs/heads/main.zip",
        license="GPLv3",
        packages=find_packages(),

        install_requires=[
            "matplotlib>=3.1.3"
        ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent",
            "Topic :: Education",
        ],
        entry_points={
            "console_scripts": [
                "physicscore=src:run_physicscore",
                "reportgen=src:generate_report",
            ],
        },
        package_data={
            "src": ["Physicscore.ico"],
        },
        include_package_data=True,
        platforms=["Windows", "Linux", "Mac OS-X"],
        python_requires='>=3.6'
    )
