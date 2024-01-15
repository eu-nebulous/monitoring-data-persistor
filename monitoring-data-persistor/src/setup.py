from setuptools import setup, find_packages

setup(
    name='monitoring-data-persistor',
    version='1.0.0',
    #packages=find_packages('.'),
    packages=["main","main.exn","main.exn.core","main.exn.handler","main.exn.settings","main.runtime"],

package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'start_exsmoothing = main.runtime:DataPersistor',
        ],
    }
    # other setup configurations
)
