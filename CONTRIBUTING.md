Thank you for wanting to contribute to PolicyEngine! :smiley:

In addition to this guide, [this document](https://docs.google.com/document/d/1BiajMUJZFzG24Ju5lTybCAW8tp59B3E_DNhS8eJkuR0/edit) contains suggestions on developing tax-benefit programs in PolicyEngine.

TL;DR: [GitHub Flow](https://guides.github.com/introduction/flow/), [SemVer](http://semver.org/).

## Onboarding: Installation

## Set up CodeSpaces for PolicyEngine

1. If you haven't already, fork the [**PolicyEngine/policyengine-us**](http://github.com/PolicyEngine/policyengine-us) repository to your personal account
> Leave the **Copy the master branch only** box checked <br>

1. From **GitHub Codespaces** (https://github.com/codespaces), click **New codespace**
1. Select  **yourusername/policyengine-us** as the repository and all other defaults
1. Create new codespace from blanck template
1. In the terminal, type `conda create -n policyengine python=3.9 -y`
1. In the terminal, type `conda init`
1. Restart terminal (click the bin icon to delete the terminal, and start a new terminal from the menu on top)
1. In the new terminal, type `conda activate policyengine`
1. In the same terminal, type `make install`
1. Check out the issue you want to work on<br>
   *If no issue, create one at https://github.com/policyengine/policyengine-us, or from the GitHub extension in Codespaces*
1. After making any changes, run `make test` in the terminal to test<br>
   This sometimes fails with **[Makefile:9: test] Killed** after a while
   To run a specific test or folder of tests, run `policyengine-core test [path]`
   Optionally with `-v` to get verbose output (the computation tree)

1. When returning to the Codespace:
    1. Return to GitHub Codespaces
    1. Open the codespace you previously made
    1. Open terminal
    1. Run `conda activate policyengine` in the terminal<br>
       *If this fails, it means your codespaces session has expired, you need to re-run step **5-7***

**We recommend that new developers use GitHub Codespaces, but if you want to proceed with VS Code instead, see the instruction below:**

## Install and Set up VS Code

1. Install VS Code (https://code.visualstudio.com/download)
1. Install VS Code extensions (you will have to sign in to GitHub for each)
  1. GitHub Pull Requests & Issues
  1. Live Share
  1. Python
  1. *Recommended: GitHub Copilot https://github.com/features/copilot (30 day free trial)*

1. Set git username and email
1. Set git username and email<br>
   You can do so by typing the following command into the terminal:<br>
   a. `git config --global user.name "John Doe"`<br>
   b. `git config --global user.email johndoe@example.com`
1. Install conda: `conda install python=3.9`
1. Fork and clone this repository

### Extra steps for Windows users
1. Install `make`
    1. Open VS Code as administrator (search and right-click)
    1. Open a new terminal in VS Code
    1. https://chocolatey.org/install
    1. Copy the command into the temrinal
    1. In terminal, run: `choco install make`
1. Run conda https://stackoverflow.com/a/67996662/1840471
1. Run `make install` from terminal in VS Code after opening **policyengine-us**
    1. If you have multiple versions of Python installed, you may need to run `python3 -m pip install - e`
1. Change format on save for Python to black and set line length to 79
1. If you don't have conda installed, you can try the following steps on **MAC**:
    1. Install brew
    1. `brew install python`
    1. `pyenv init`
    1. `pyenv shell 3.9.16`
    1. `python -m venv venv`



## Identify and create an issue in GitHub

If you want to work on  a task that's not yet an issue, you can start by creating an issue for it. One way to do so is to log on to your github account in your browser and go to the corresponding repository. Under the **Issues** menu, you can click on **New Issue** tab. You can assign this issue to specific person/peole, and add tags for better classification purpose.

When creating a new issue, you should **specify the program rule and link to a law and/or government site (e.g. tax form)**.


## Claim an issue in VS Code
In VS Code, open the GitHub Extension. In the lower left, under the **Issues** menu, you can find the issues you would like to work on. If an issue has already been assigned to you, you can find it under **My Issues**.

When you are ready to work on it, click the right arrow to the right of the issue number and issue title **→** to start. This will assign you to the issue and create a new branch named for the issue number.


## Work on issues assigned in VS Code

Usually, you need to work on four specific types of files:

* Test (`.yaml`)
* Parameter (`.yaml`)
* Variable (`.py`)
* changelog_entry(`.yaml`)

**You can follow the procedure below to tackle them:**

**1. Create a unit test**
This will be a file in *policyengine_{country}/tests/[path to program]/variable.yaml*. We apply **test driven development**, where we write tests before writing the logic. This means tests will break and the goal of the Pull Request (**PR**) is to pass the tests. Unit tests specify direct inputs to the variable for a number of cases, and the expected output.

**2. Commit your changes**
Use the VS Code source control extension to enter a message, such as *"Create unit test for ['variable']"* and click **Commit**.

**3. Populate changelog_entry (.yaml)**

This file describes the changes. And is usually in the following format:
```yaml
- bump: {major, minor, patch}
  changes:
    {added, removed, changed, fixed}:
      - <variable or program>
```

Refer to the [semantic versioning](http://semver.org/) spec and https://keepachangelog.com for more information.


**4. Commit your changes again**
Enter the commit message: *"Populate changelog_entry.yaml"*

**5. Publish branch and Draft a Pull Request (PR)**

Before creating a pull request, type `git pull upstream master` in your terminal to make sure you  are using the latest version of the repository.

**Publishing a branch** means to publish to origin (your fork). When you are ready to submit a pull request, VS Code will ask if you want to create a pull request. Click the button to do so. Enter a title describing what the completed PR will contribute, e.g., **"Add [variable or program]"**. then add to the body **"Fixes #[issue]** to link the PR to the issue such that merging the PR will close the issue.

Finally, check the box for **"Draft"** indicating that the PR is not yet ready to merge.

We follow the [GitHub Flow](https://guides.github.com/introduction/flow/): all code contributions are submitted via a pull request towards the `master` branch.

Opening a Pull Request means you want that code to be merged. If you want to only discuss it, send a link to your branch along with your questions through whichever communication channel you prefer.

**6. Run `make test` from the terminal**

The new tests will fail, but after successfully completing the remianing steps, they will pass.

**7. Create the policy parameters**

Parameters are **features of the rules defined in the law**. They can be numbers, bools, or lists, and htey can also break down by categories or vary with respect to quantitative variables. [You can check here for more details.](https://openfisca.org/doc/coding-the-legislation/legislation_parameters.html#creating-scales)


One common breakdown is to break down by **`filing_status`**. If you decided to include such category, it is important to make sure that you include all five categories as follows:

* `SINGLE`
* `SEPARATE`
* `SURVIVING_SPOUSE`
* `HEAD_OF_HOUSEHOLD`
* `JOINT`

Sometimes, the document that you refer to (e.g. tax instruction) does not specify all five statuses. In that case, you can let the `SURVIVING_SPOUSE` cases to be the same as the `JOINT` case.

PolicyEngine defines parameters as yaml files, which specify the values as of certain dates, as well as metadata on the units and reference(s).

**8. Create the variable logic**

Variables are features of each person or household, and PolicyEngine defines them as Python files. Create a file in the variables tree corresponding to the program, such as `my_tax_credit.py`, and copy an existing `.py` file as template. Variables are instances of the Variable class, which defines attributes like the entity and reference, and a formula method defining the logic.

One minor thing that might be helpful:

When you are trying to define a condition, use a `where` statement instead of an `if` statement. Similarly, use `max_` and `min_` (aliases for `numpy.maximum` and `numpy.maximum`) instead of `max` and `min`. These are needed for vectorization.

**Make sure your `variable.py` file has the same name as the corresponding `test.yaml` file!**

This will also match the variable name as defined in the class.

**9. Run `make test` again**
To run a specific yaml test or folder of yaml tests, run `policyengine-core test [path] -c policyengine_us`

**10. Run `make format`**

This will align the code to the black Python formatting standard, and ensure each file ends in an empty new line.

**Remember to run `git pull upstream master` every time before you *Sync* or *Create a new PR* **


### Peer reviews

All pull requests must be reviewed by someone else than their original author.

> In case of a lack of available reviewers, one may review oneself, but only after at least 24 hours have passed without working on the code to review.

To help reviewers, make sure to add to your PR a **clear text explanation** of your changes.

In case of breaking changes, you **must** give details about what features were deprecated.

> You must also provide guidelines to help users adapt their code to be compatible with the new version of the package.
