from setuptools import find_packages, setup

with open('VERSION.txt') as fp:
    version = fp.read().strip()

with open('README.md') as fp:
    readme = fp.read()

with open('requirements.txt') as fp:
    requirements = fp.read().splitlines()

setup(
    name='mccq',
    version=version,
    author='Arcensoth',
    author_email='arcensoth@gmail.com',
    url='https://github.com/Arcensoth/mccq',
    license='MIT',
    description='Minecraft command query program. Inspired by the in-game help command, with added features like multiple version support and expandable regex search.',
    long_description_content_type='text/markdown',
    long_description=readme,
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.6',
    keywords='minecraft command query help utility',
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
    )
)
