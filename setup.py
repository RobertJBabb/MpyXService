from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='MpyXService',
    version='0.0.1',
    author="Robert J Babb",
    author_email="rjb_github@dragonflythingworks.com",
    description="A simple mpy-cross web service",
    long_description=long_description,
    url="https://github.com/RobertJBabb/MpyXService",
    # packages=['mpyxservice'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'gunicorn',
        'mpy-cross',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
)
