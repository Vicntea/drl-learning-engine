from setuptools import setup, find_packages

setup(
    name="drl_learning_engine",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "gymnasium",
        "stable-baselines3"
    ],
)