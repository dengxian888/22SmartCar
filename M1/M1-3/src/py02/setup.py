from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'py02'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ljx',
    maintainer_email='1741538922@qq.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'static_tf_broadcaster = py02.static_tf_broadcaster:main',
            'time_observer = py02.time_observer:main',
            'sync_node = py02.sync_node:main',
        ],
    },
)
