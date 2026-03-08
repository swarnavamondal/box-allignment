from setuptools import find_packages, setup

package_name = 'align_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='swarnava',
    maintainer_email='swarnavamondal2005@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "test_node = align_pkg.sample_node:main",
            "publish_node = align_pkg.publish_node:main",
            "kfs_alignment_node = align_pkg.kfs_alignment_node:main",
        ],
    },
)
