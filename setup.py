from setuptools import setup, find_packages

setup(
    name="sb-stealth-wrapper",
    version="0.1.1",
    description="A robust, plug-and-play wrapper around SeleniumBase UC Mode for stealth web automation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dhiraj Das",
    author_email="dhirajdas.666@gmail.com",
    url="https://github.com/godhiraj-code/stealthautomation/",
    packages=find_packages(),
    install_requires=[
        "seleniumbase",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
