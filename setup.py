from setuptools import setup, find_packages

setup(
    name='resorter',
    version='0.1.0',
    description='file arranger',
    long_description='',
    long_description_content_type='text/markdown',
    url='https://github.com/0x656b694d/resorter',
    author='Michaël',
    author_email='smartptr@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License, version 3',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    extras_require={
        },
    scripts=["src/resort"],
    entry_points={
        'console_scripts': [
            'resorter=resort:main',
            ],
        }
    )

