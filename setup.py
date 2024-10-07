import setuptools

with open("PYPI_README.rst", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="CrossRename",
	version="1.0.0",
	author="Emmanuel C. Jemeni",
	author_email="jemenichinonso11@gmail.com",
	description="Harmonize file names for Linux and Windows.",
	long_description=long_description,
	long_description_content_type="text/x-rst",
	url="https://github.com/Jemeni11/CrossRename",
	project_urls={
		"Bug Tracker": "https://github.com/Jemeni11/CrossRename/issues",
	},
	entry_points={
		'console_scripts': [
			'crossrename=CrossRename.main:main'
		]
	},
	install_requires=[],
	keywords="files rename linux windows transferring filename",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	packages=setuptools.find_packages('.'),
	python_requires=">=3.6"
)
