from distutils.core import setup

setup(
    name='uw-course-catalog',
    version='1.0.0',
    url='https://github.com/kjiwa/uw-course-catalog',
    license='MIT',
    author='Kamil Jiwa',
    author_email='kamil.jiwa@gmail.com',
    description='Exports courses from the UW course catalog to CSV.',
    install_requires=['lxml', 'titlecase'])
