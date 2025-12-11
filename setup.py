# setup.py
from setuptools import setup, find_packages

setup(
    name="LaiCai",
    version="0.1",
    package_dir={"":"src"},
    packages=find_packages(),
    py_modules=["db"],  # 单独的模块文件
)