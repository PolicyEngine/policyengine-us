> This file defines the rules to follow to contribute to your repository.
> The rules suggested here are what we generally use for OpenFisca country packages.
> You can of course edit them, and you should probably remove this block :)

Thank you for wanting to contribute to OpenFisca! :smiley:

TL;DR: [GitHub Flow](https://guides.github.com/introduction/flow/), [SemVer](http://semver.org/).


## Pull requests

We follow the [GitHub Flow](https://guides.github.com/introduction/flow/): all code contributions are submitted via a pull request towards the `master` branch.

Opening a Pull Request means you want that code to be merged. If you want to only discuss it, send a link to your branch along with your questions through whichever communication channel you prefer.

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

OpenFisca-Country-Template changes must be understood by users who don't necessarily work on the code. The Changelog must therefore be as explicit as possible.

Each change must be documented with the following elements:

- On the first line appears as a title the version number, as well as a link towards the Pull Request introducing the change. The title level must match the incrementation level of the version.


> For instance :
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
> - Impacted periods: Until 31/12/2015.
> - Impacted areas: `benefits/healthcare/universal_coverage`

- Finally, for all cases except `Minor Change`, the changes must be explicited by details given from a user perspective: in which case was an error or a problem was noticed ? What is the new available feature ? Which new behaviour is adopted.

> For instance:
>
> * Details :
>   - These variables now return a yearly amount (instead of monthly):
>     - `middle_school_scholarship`
>     - `high_school_scholarship`
>   - _The previous monthly amounts were just yearly amounts artificially divided by 12_
>
> or :
>
> * Details :
>  - Use OpenFisca-Core `12.0.0`
>  - Change the syntax used to declare parameters:
>      - Remove "fuzzy" attribute
>      - Remove "end" attribute
>      - All parameters are assumed to be valid until and end date is explicitely specified with an `<END>` tag

When a Pull Request contains several disctincts changes, several paragraphs may be added to the Changelog. To be properly formatted in Markdown, these paragraphs must be separated by `<!-- -->`.
