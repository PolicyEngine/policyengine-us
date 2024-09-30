## Variables

- Useful variable classes:
    - [Adjusted gross income](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/gov/irs/income/taxable_income/adjusted_gross_income/adjusted_gross_income.py)
    - [Exemptions](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/gov/irs/income/taxable_income/exemptions.py)
    - [Dependents in tax unit](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/demographic/tax_unit/tax_unit_dependents.py)
    - [Is a dependent (person level)](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/demographic/tax_unit/is_tax_unit_dependent.py)

- Add readme.md files to state program variable folders per [this PR](https://github.com/PolicyEngine/policyengine-us/pull/2740)
    - Eliminate abbreviations on the front end

- Dividing by 0 Problem
    - [PR example](https://github.com/PolicyEngine/policyengine-us/pull/2561/files) to overcome /0 
    - Mask example:
        - Use when a division can lead to a “dividing by 0” issue
