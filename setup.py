import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slack_pybot",
    version="0.0.3",
    author="Albert Wu",
    author_email="albertywu@gmail.com",
    description="slackbot written in python 3.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/albertywu/pybot",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
