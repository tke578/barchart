from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='barchart',
	    packages=['barchart'],
      version='',
      description='The Unofficial API for barchart.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/tke578/barchart',
      author='Andrew Garcia',
      author_email='tke578@gmail.com',
      keywords = ['barchart', 'api', 'screener', 'barchart api', 'options', 'unusual options activity'],
      license='MIT',
      install_requires=[
          'requests_html',
          'async',
          'user_agent',
          'pyppeteer'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)