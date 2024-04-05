from setuptools import setup, find_packages

setup(
    name='monitoring-data-persistor',
    version='1.0.0',
    #packages=find_packages('.'),
    packages=["main","exn","exn.core","exn.handler","exn.settings","main.runtime"],

package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'start_dp = main.runtime:DataPersistor',
        ],
    }
    # other setup configurations
)
