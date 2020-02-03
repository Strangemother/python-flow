from setuptools import setup, find_packages

import os
abs_src = os.path.abspath('./src')
setup(name='flow',
    version='0.1',
    description='Simple Multiprocessing Queue',
    url='http://github.com/strangemother/flow',
    author='Jay Jagpal',
    author_email='jay@strangemother.com',
    license='MIT',
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'django',
        'huey',
        'gevent',
        'colorama',
        ],
    classifiers=[
      'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            # flow-consumer flow.machine.main.huey -k greenlet -w 16
            'flow-consumer=flow.consumer:consumer_main',
            'flow-machine=flow.consumer:consumer_default_main',
        ],
    },
    #package_dir={'': 'src/'},  # Optional
    #packages=find_packages(where='src'),  # Required
    zip_safe=True)
