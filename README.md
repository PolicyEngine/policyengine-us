# OpenFisca Country-Template

This repository helps you quickly bootstrap and use your own OpenFisca country package.

**You should NOT fork it but [download a copy](https://github.com/openfisca/country-template/archive/master.zip) of it** and follow the bootstrapping instructions below.

> Otherwise, you will have to clean up all tags when you deploy your own country package.


## Bootstrapping your Country Package

This set of instructions will create your own copy of this boilerplate directory and customise it to the country you want to work on. You will need to have [Git](https://git-scm.com) installed.

1. [download a copy](https://github.com/openfisca/country-template/archive/master.zip) of this repository, unzip it and `cd` into it in a Terminal window.

2. Create a new repository on your favourite git host (Github, Bitbucket, GitLab, etc) with the name openfisca-your_country_name. For example, `openfisca-france`.

3. Set up the two following variables and execute the `bootstrap.sh` script to initialise the git repository and replace all references to `openfisca_country_template` with references to your new country package in the code base:

```sh
export COUNTRY_NAME=France  # set the name of your country here; you should keep all capitals, and replace any spaces in the name by underscores
export REPOSITORY_URL=https://github.com/YOUR_ORGANISATION/OpenFisca-$COUNTRY_NAME  # set here the URL of the repository you created in step 2.
./bootstrap.sh
```

4. Push your changes to your git host:

```sh
git push origin master
```

That's it, you're all set!

## Writing the Legislation

The country whose law is modelled here has a very simple tax and benefit system.

- It has a flat rate tax whose rates increase every year.
- On the first of December, 2015, it introduced a basic income for all its citizens of age who have no income.
- On the first of December, 2016, it removed the income condition, providing all its adult citizens with a basic income.

These elements are described in different folders. All the modelling happens within the `openfisca_country_template` folder.

- The rates are in the `parameters` folder.
- The formulas are in the `variables` folder.
- This country package comes also with *reforms* in the `reforms` folder. This is optional: your country may exist without defining any reform.
    - In this country, there is [a reform project](./openfisca_country_template/reforms/modify_social_security_taxation.py) aiming to modify the social security taxation, deleting the first bracket, raising the intermediary ones and adding a new bracket with a higher tax rate of `40 %` for people earning more than `40000`. This reform project would apply starting from `2017-01-01`.

The files that are outside from the `openfisca_country_template` folder are used to set up the development environment.

## Packaging your Country Package for Distribution

Country packages are python distributions. To distribute your package via `pip`, follow the steps given by the [Python Packaging Authority](https://python-packaging-user-guide.readthedocs.io/tutorials/distributing-packages/#packaging-your-project).

## Install Instructions for Users and Contributors

This package requires [Python 3.7](https://www.python.org/downloads/release/python-370/). More recent versions should work, but are not tested.

All platforms that can execute Python are supported, which includes GNU/Linux, macOS and Microsoft Windows (in which case we recommend using [ConEmu](https://conemu.github.io/) instead of the default console).

### Setting-up a Virtual Environment with Pew

In order to limit dependencies conflicts, we recommend to use a [virtual environment](https://virtualenv.pypa.io/en/stable/) (abbreviated as “virtualenv”) with a virtualenv manager such as [pew](https://github.com/berdario/pew).

- A [virtualenv](https://virtualenv.pypa.io/en/stable/) is a project specific environment created to suit the needs of the project you are working on.
- A virtualenv manager such as [pew](https://github.com/berdario/pew) lets you easily create, remove and toggle between several virtualenvs.

To install pew, launch a terminal on your computer and follow these instructions:

```sh
pip install --upgrade pip
pip install pew  # if asked, answer "Y" to the question about modifying your shell config file.
pew new openfisca --python=python3.7  # create a new virtualenv called “openfisca”
```

The virtualenv you just created will be automatically activated. This means you will operate in the virtualenv immediately. You should see a prompt resembling this:

```
Installing setuptools, pip, wheel...done.
Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
```

You can re-activate that virtualenv at any time with `pew workon openfisca`.

:tada: You are now ready to install this OpenFisca Country Package!

Two install procedures are available. Pick procedure A or B below depending on how you plan to use this Country Package.

### A. Minimal Installation (Pip Install)

Follow this installation if you wish to:
- run calculations on a large population;
- create tax & benefits simulations;
- write an extension to this legislation (e.g. city specific tax & benefits);
- serve your Country Package with the OpenFisca Web API.

For more advanced uses, head to the [Advanced Installation](#advanced-installation-git-clone).

#### Install this Country Package with Pip Install

Inside your virtualenv, check the prerequisites:

```sh
python --version  # should print "Python 2.7.xx".
#if not, make sure you pass the python version as an argument when creating your virtualenv
```

```sh
pip --version  # should print at least 9.0.
#if not, run "pip install --upgrade pip"
```
Install the Country Package:

```sh
pip install openfisca_country_template
```

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To learn how to use OpenFisca, follow our [tutorials](https://openfisca.org/doc/).
- To serve this Country Package, serve the [OpenFisca web API](#serve-your-country-package-with-the-openFisca-web-api).

Depending on what you want to do with OpenFisca, you may want to install yet other packages in your virtualenv:
- To install extensions or write on top of this Country Package, head to the [Extensions documentation](https://openfisca.org/doc/contribute/extensions.html).
- To plot simulation results, try [matplotlib](http://matplotlib.org/).
- To manage data, check out [pandas](http://pandas.pydata.org/).

### B. Advanced Installation (Git Clone)

Follow this tutorial if you wish to:
- create or change this Country Package's legislation;
- contribute to the source code.

#### Clone this Country Package with Git

First of all, make sure [Git](https://www.git-scm.com/) is installed on your machine.

Set your working directory to the location where you want this OpenFisca Country Package cloned.

Inside your virtualenv, check the prerequisites:

```sh
python --version  # should print "Python 2.7.xx".
#if not, make sure you pass the python version as an argument when creating your virtualenv
```

```sh
pip --version  # should print at least 9.0.
#if not, run "pip install --upgrade pip"
```
Clone this Country Package on your machine:

```sh
git clone https://github.com/openfisca/openfisca-country-template.git
cd openfisca-country-template
pip install --editable .[dev]
```

You can make sure that everything is working by running the provided tests with `make test`.

> [Learn more about tests](https://openfisca.org/doc/coding-the-legislation/writing_yaml_tests.html)

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To write new legislation, read the [Coding the legislation](https://openfisca.org/doc/coding-the-legislation/index.html) section to know how to write legislation.
- To contribute to the code, read our [Contribution Guidebook](https://openfisca.org/doc/contribute/index.html).

## Serve this Country Package with the OpenFisca Web API

If you are considering building a web application, you can use the packaged OpenFisca Web API with your Country Package.

To serve the Openfisca Web API locally, run:

```sh
openfisca serve --port 5000
```

Or use the quick-start Make command:

```
make serve-local
```

To read more about the `openfisca serve` command, check out its [documentation](https://openfisca.org/doc/openfisca-python-api/openfisca_serve.html).

You can make sure that your instance of the API is working by requesting:

```sh
curl "http://localhost:5000/spec"
```

This endpoint returns the [Open API specification](https://www.openapis.org/) of your API.

:tada: This OpenFisca Country Package is now served by the OpenFisca Web API! To learn more, go to the [OpenFisca Web API documentation](https://openfisca.org/doc/openfisca-web-api/index.html).

You can test your new Web API by sending it example JSON data located in the `situation_examples` folder.

Substitute your package's country name for `openfisca_country_template` below:

```sh
curl -X POST -H "Content-Type: application/json" \
  -d @./openfisca_country_template/situation_examples/couple.json \
  http://localhost:5000/calculate
```