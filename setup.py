from setuptools import setup, find_packages


def load_requirements(use_case):
    """
    Loading range requirements.
    Packaging should be used for installing the package into existing stacks.
    We therefore read the .in file for the use case.
    .txt files include the exact pins, and are useful for deployments with
    exactly comparable environments.
    """
    reqs = []
    with open("requirements/%s.in" % use_case, "r") as f:
        reqs = [
            req
            for req in f.read().splitlines()
            if not req.strip() == ""
            and not req.strip().startswith("#")
            and not req.strip().startswith("-c")
            and not req.strip().startswith("--find-links")
        ]
    return reqs


setup(
    name="flexmeasures-weather",
    description="Integrating FlexMeasures with multiple API services",
    author="Seita Energy Flexibility BV",
    author_email="nicolas@seita.nl",
    url="https://github.com/FlexMeasures/flexmeasures-weather",
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
