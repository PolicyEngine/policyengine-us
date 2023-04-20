Thank you for wanting to contribute to OpenFisca! :smiley:

TL;DR: [GitHub Flow](https://guides.github.com/introduction/flow/), [SemVer](http://semver.org/).

## Onboarding: Installation

## Set up CodeSpaces for PolicyEngine

1. If you haven't already, fork the **PolicyEngine/policyengine-us**(http://github.com/PolicyEngine/policyengine-us) repository to your personal account
> Leave the **Copy the master branch only** box checked <br>

2. From **GitHub Codespaces** (https://github.com/codespaces), click **New codespace**
3. Select  **yourusername/policyengine-us** as the repository and all other defaults
4. Create new codespace from blanck template
5. In the terminal, type `conda create -n policyengine python=3.9 -y`
6. In the terminal, type **conda init**
7. Restart terminal (click the bin icon to delete the terminal, and start a new terminal from the menu on top)
8. In the new terminal, type **conda activate policyengine**
9. In the same terminal, type **make install**
10. Check out the issue you want to work on
>If no issue, create one at github.com/policyengine/policyengine-us, or from the GitHub extension in Codespaces <br>
11. After making any changes, run **make test** in the temrinal to test
>This sometimes fails with **[Makefile:9: test] Killed** after a while
>To run a specific test or folder of tests, run **policyengine-core test [path]**
>Optionally with **-v** to get verbose output (the computation tree)

12. When returning to the Codespace:
  1. Return to GitHub Codespaces
  2. Open the codespace you previously made
  3. Open terminal
  4. Run **conda activate policyengine** in the temrinal
    >> If this fails, it means your codespaces session has expired, you need to re-run step **5-7**

**We recommend that new developers use GitHub Codespaces, but if you want to proceed with VS Code instead, see the instruction below:**

## Install and Set up VS Code

1. Install VS Code (https://code.visualstudio.com/download)
2. Install VS Code extensions (you will have to sign in to GitHub for each)
> 1. GitHub Pull Requests & Issues extension
> 2. Live ShareInstall
> 3. Python extension
> 4. [Recommended]: GitHub Copilot https://github.com/features/copilot (30 day free trial)

3. Set git username and email
4. Set git username and email
> You can do so by typing the following command into the terminal:
>> a. **git config --global user.name "John Doe"**
>> b. **git config --global user.email johndoe@example.com**
4. Install conda
>> **conda install python-3.9**
5. Fork and clone country package you're working on:
> a. github.com/policyengine/policyengine-us <br>
> b. github.com/policyengine/policyengine-canada<br>
> c. Fork <br>
> d. github.com/policyengine/policyengine-ng <br>
6. Extra steps for Windows users
a. Install make
>> i. Open VS Code as administrator (search and right-click) <br>
>> ii. Open a new terminal in VS Code<br>
>> iii. https://chocolatey.org/install<br>
>> iv. Copy the command into the temrinal<br>
>> v. In terminal, run: **choco install make**<br>
b. Run conda https://stackoverflow.com/a/67996662/1840471<br>
7. Run **make install** from terminal in VS Code after opening **policyengine-us**
>>a. If you have multiple versions of Python installed, you may need to run **python3 -m pip install - e**
8. Change format on save for Python to black and set line length to 79
9. If you don't have conda installed, you can try the following steps on **MAC**:
>> 1. Install brew
>> 2. **brew install python**
>> 3. **pyenv init**
>> 4. **pyenv shell 3.9.16**
>> 5. **python -m venv venv**



## Identify and Creat an Issue in Github

If you want to work on  a task that's not yet an issue, you can start by creating an issue for it. One way to do so is to log on to your github account in your browser and go to the corresponding repository. Under the **Issues** menu, you can click on **New Issue** tab. You can assign this issue to specific person/peole, and add tags for better classification purpose.

When creating a new issue, you should **specify the program rule and link to a law and/or government site (e.g. tax form)**.


## Claim a issue in VS Code
In VS Code, open the GitHub Extension. In the lower left, under the **Issues** menu, you can find the issues you would like to work on. If an issue has already been assigned to you, you can find it under **My Issues**.

When you are ready to work on it, click the right arrow to the right of the issue number and issue title **→** to start. This will assign you to the issue and create a new branch named for the issue number.


## Work on issues assigned in VS Code:

Usually, there are four sepcific types of files you will need to work on:

* Test (.yaml)
* Parameter (.yaml)
* Variable (.py)
* changelog_entry(.yaml)

**You can follow the procedure below to tackle them:** <br>
**1. Create a unit test** <br>
This will be a file in *policyengine_{country}/tests/[path to program]/variable.yaml*. We apply **test driven development**, where we write tests before writing the logic. This means tests will break and the goal of the Pull Request (**PR**) is to pass the tests. Unit tests specify direct inputs tot he variable for a number of cases, and the expected output.

**2. Commit your changes** <br>
Use the VS Code source control extension to enter a message, such as *"Create unit test for ['variable']"* and click **Commit**.

**3. Populate changelog_entry (.yaml)**<br>
This file describes the changes. And is usaully in the following format:
> -bump: <br>
>>changes: <br>
>>added: <br>

*You can refer to the section below for more details.*<br>

**4. Commit your changes again** <br>
Enter the commit message: *"Populate changelog_entry.yaml"*

**5. Publish branch and Draft a Pull Request (PR)**<br>
Before creating a pull request, type **git pull upstream master** in your terminal to make sure you  are using the latest version of the repository.
**Publishing a branch** means to publich to origin (your fork). When you are ready to submit a pull request, VS Code will ask if you want to create a pull request. Click the button to do so. Enter a title describing what the completed PR will contribute, e.g., **"Add [variable or program]"**. then add to the body **"Fixes #[issue]** to link the PR to the issue such that merging the PR will close the issue.

Finally, check the box for **"Draft"** indicating that the PR is not yet ready to merge.

We follow the [GitHub Flow](https://guides.github.com/introduction/flow/): all code contributions are submitted via a pull request towards the `master` branch.

Opening a Pull Request means you want that code to be merged. If you want to only discuss it, send a link to your branch along with your questions through whichever communication channel you prefer.

**6. Run "make test" from the terminal**<br>
The new tests will fial, but after successfully completing the remianing steps, they will pass.

**7. Create the policy parameters**<br>
Parameters are **features of the rules defined in the law**. They can be numbers, bools, or lists, and htey can also break down by categories or vary with respect to quantitative variabels (https://openfisca.org/doc/coding-the-legislation/legislation_parameters.html#creating-scales) [you can check here for more details.] <br>


One common breakdown is to break down by **"filing_status"**. If you decided to include such category, it is important to make sure that you include all five categories as follow: <br>

* SINGLE
* SEPARATE
* WIDOW
* HEAD_OF_HOUSEHOLD
* JOINT

Sometimes, the document that you refer to (e.g. tax instruction) does not specify all five statuses. In that case, you can let the **“WIDOW”**， **“HEAD_OF_HOUSEHOLD"** cases to be the same as the "SINGLE" case.

PolicyEngine defines parameters as yaml files, which specify the values as of certain dates, as well as metadata on the units and reference(s).

**8. Create the variable logic**<br>
Variables are features of each person or household, and PolicyEngine defines them as Python files. Create a file in the variables tree corresponding to the program, such as **"my_tax_credit.py"**, and copy an existing .py file as template. Variables are instances of the Variable class, which defines attributes like the entity and reference, and a formula method defining the logic.

One minor thing that might be helpful: <br>

When you are trying to define a condition, use *where** statement instead of **if** statement. Similarly, use **max_** and **min_** instead of **max** and **min**. These are needed for vectorization.

**Make sure your variable.py file has the same name as the corresponding test.yaml file!**

**9. Run *make test* again**
To run a specific yaml test or folder of yaml tests, run **policyengine-core test [path] -c policyengine_us.**

**10. Run *make format***<br>
This will align the code ot the black Python formatting standard, and ensure each file ends in an empty new line. <br>

**Again, remember to run **git pull upstream master** everytime before you *Sync* or *Creating a new PR* **


### Peer reviews

All pull requests must be reviewed by someone else than their original author.

> In case of a lack of available reviewers, one may review oneself, but only after at least 24 hours have passed without working on the code to review.

To help reviewers, make sure to add to your PR a **clear text explanation** of your changes.

In case of breaking changes, you **must** give details about what features were deprecated.

> You must also provide guidelines to help users adapt their code to be compatible with the new version of the package.

## Advertising changes

### Version number

We follow the [semantic versioning](http://semver.org/) spec: any change impacts the version number, and the version number conveys API compatibility information **only**.

Examples:

#### Patch bump

- Fixing or improving an already existing calculation.

#### Minor bump

- Adding a variable to the tax and benefit system.

#### Major bump

- Renaming or removing a variable from the tax and benefit system.

### Changelog

PolicyEngine US changes must be understood by users who don't necessarily work on the code. The Changelog must therefore be as explicit as possible.

Each change must be documented with the following elements:

- On the first line appears as a title the version number, as well as a link towards the Pull Request introducing the change. The title level must match the incrementation level of the version.

> For instance :
>
> # 13.0.0 - [#671](https://github.com/openfisca/openfisca-france/pull/671)
>
> ## 13.2.0 - [#676](https://github.com/openfisca/openfisca-france/pull/676)
>
> ### 13.1.5 - [#684](https://github.com/openfisca/openfisca-france/pull/684)

- The second line indicates the type of the change. The possible types are:
- `Tax and benefit system evolution`: Calculation improvement, fix, or update. Impacts the users interested in calculations.
- `Technical improvement`: Performances improvement, installing process change, formula syntax change… Impacts the users who write legislation and/or deploy their own instance.
- `Crash fix`: Impact all reusers.
- `Minor change`: Refactoring, metadata… Has no impact on users.

- In the case of a `Tax and benefit system evolution`, the following elements must then be specified:
  - The periods impacted by the change. To avoid any ambiguity, the start day and/or the end day of the impacted periods must be precised. For instance, `from 01/01/2017` is correct, but `from 2017` is not, as it is ambiguous: it is not clear wheter 2017 is included or not in the impacted period.
  - The tax and benefit system areas impacted by the change. These areas are described by the relative paths to the modified files, without the `.py` extension.

> For instance :
>
> - Impacted periods: Until 31/12/2015.
> - Impacted areas: `benefits/healthcare/universal_coverage`

- Finally, for all cases except `Minor Change`, the changes must be explicited by details given from a user perspective: in which case was an error or a problem was noticed ? What is the new available feature ? Which new behaviour is adopted.

> For instance:
>
> - Details :
>   - These variables now return a yearly amount (instead of monthly):
>     - `middle_school_scholarship`
>     - `high_school_scholarship`
>   - _The previous monthly amounts were just yearly amounts artificially divided by 12_
>
> or :
>
> - Details :
>
> * Use OpenFisca-Core `12.0.0`
> * Change the syntax used to declare parameters:
>   - Remove "fuzzy" attribute
>   - Remove "end" attribute
>   - All parameters are assumed to be valid until and end date is explicitely specified with an `<END>` tag

When a Pull Request contains several disctincts changes, several paragraphs may be added to the Changelog. To be properly formatted in Markdown, these paragraphs must be separated by `<!-- -->`.

