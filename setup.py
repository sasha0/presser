from setuptools import setup

setup(
    name='presser',
    license='BSD',
    version='0.1',
    url='https://github.com/sasha0/presser',
    author='Alexander Gaevsky',
    py_modules=['benchmark', 'constants', 'presser'],
    install_requires=[
        'grequests',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'presser=presser:main'
        ]
    }
)