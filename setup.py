import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='camset',
    version='0.0.20',
    author='Dennis Hägg',
    description='GUI for v4l2-ctl',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/azeam/camset',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
    ],
    data_files=[
        ('share/applications', ['res/camset.desktop']),
        ('share/icons', ['res/camset.png']),
    ],
    python_requires='>=3.0, <4',
    install_requires=['opencv-python', 'PyGObject'],
    entry_points={
        'console_scripts': [
            'camset=camset.camset:main',
        ],
    }
)
