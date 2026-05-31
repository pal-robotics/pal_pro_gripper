from setuptools import find_packages, setup, glob
import os
package_name = 'pal_pro_gripper_wrapper'

setup(
    name=package_name,
    version='1.12.5',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), ['config/gripper.yaml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer=['MVI'],
    maintainer_email=['matteo.villani@pal-robotics.com'],
    license='Apache License, Version 2.0',
    description='Grasp controller to close with a determined error on position only\
    so to skip overheating.',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gripper_grasper_srv = pal_pro_gripper_wrapper.gripper_grasper_srv:main'
        ],
    },
)
