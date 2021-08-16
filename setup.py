"""
Project KINETIC, setup script for package generation.

██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Made by perpetualCreations
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="project-kinetic",
    version="1.1",
    author="perpetualCreations",
    author_email="tchen0584@gmail.com",
    description="Control modular and configurable robotic agents over the"
    " network.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perpetualCreations/kinetic/",
    install_requires=["swbs > 1.2", "pyserial", "numpy",
                      "opencv-contrib-python", "imutils", "sense-hat",
                      "gpiozero"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
