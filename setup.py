from setuptools import setup, find_packages


def load_requirements(use_case):
    reqs = []
    with open("requirements/%s.txt" % use_case, "r") as f:
        reqs = [
            req
            for req in f.read().splitlines()
            if not req.strip() == ""
            and not req.strip().startswith("#")
            and not req.strip().startswith("-c")
        ]
    return reqs


setup(
    name="flexmeasures-openweathermap",
    description="Integrating FlexMeasures with OpenWeatherMap",
    author="Seita Energy Flexibility BV",
    author_email="nicolas@seita.nl",
    url="https://github.com/SeitaBV/flexmeasures-openweathermap",
    keywords=["flexmeasures", "energy flexibility"],
    install_requires=load_requirements("app"),
    tests_require=load_requirements("test"),
    setup_requires=["pytest-runner", "setuptools_scm"],
    use_scm_version={"local_scheme": "no-local-version"},  # handled by setuptools_scm
    packages=find_packages(),
    include_package_data=True,  # setuptools_scm takes care of adding the files in SCM
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    long_description="""\
""",
)
