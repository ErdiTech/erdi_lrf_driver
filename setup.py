from glob import glob

from setuptools import find_packages, setup

package_name = 'erdi_lrf_ros2'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    # The ERDI serial codec is bundled (erdi_lrf_ros2/_erdi_lrf), so the only
    # runtime dependency is pyserial (rosdep key: python3-serial).
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='ERDI Technology',
    maintainer_email='tommy@erdimail.com',
    description='ROS 2 driver for ERDI UART laser rangefinder modules.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'erdi_lrf_node = erdi_lrf_ros2.erdi_lrf_node:main',
            # alias kept for users of the former ErdiTech/erdi-lrf-drivers package
            'range_node = erdi_lrf_ros2.erdi_lrf_node:main',
        ],
    },
)
