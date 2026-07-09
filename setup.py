from setuptools import find_packages, setup
from typing import List


def get_requirements() -> List[str]:
    requirements_lst = []

    try:
        with open("requirements.txt", "r") as file:
            requirements_lst = file.readlines()
            requirements_lst = [req.strip() for req in requirements_lst if req.strip() and not req.strip().startswith("#")]

            if "-e ." in requirements_lst:
                requirements_lst.remove("-e .")

    except FileNotFoundError as e:
        print(f"Requirements file not found: {e}")

    return requirements_lst

setup(
    name="Network Security",
    version="0.0.1",
    author = "Sriman Soma",
    author_email = "srimansoma3@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)

