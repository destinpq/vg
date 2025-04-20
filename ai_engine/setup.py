from setuptools import setup, find_packages

setup(
    name="ai_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "opencv-python>=4.7.0",
        "moviepy>=1.0.3",
    ],
    description="AI Engine for Mochi-1 Video Generation",
    author="Video Generator",
) 