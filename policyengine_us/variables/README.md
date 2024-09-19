## Variables

- Update the following files to add the state model into income tree:
    - [policyengine_us/variables/gov/states/tax/income/state_income_tax.py](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/gov/states/tax/income/state_income_tax.py) 
    - [policyengine_us/variables/household/income/household/household_tax_before_refundable_credits.py](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/income/household/household_tax_before_refundable_credits.py)
    - [policyengine_us/variables/household/income/household/household_refundable_tax_credits.py](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/income/household/household_refundable_tax_credits.py)
    - [policyengine_us/variables/gov/states/tax/income/state_income_tax_before_refundable_credits.py](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/gov/states/tax/income/state_income_tax_before_refundable_credits.py)
    - [policyengine-us/blob/master/policyengine_us/variables/household/income/household/household_state_income_tax.py ](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/income/household/household_state_income_tax.py)
    - [policyengine-us/modelled_policies.yaml](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/modelled_policies.yaml)
- After Martin Holmer verifies that it passes taxsim tests:
    - Delete parameters/gov/states/state/index.yaml
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
