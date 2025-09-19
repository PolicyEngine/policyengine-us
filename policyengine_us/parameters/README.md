## PARAMETERS

### Types of parameters
- Single value example
  - [USD Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/dc/tax/income/credits/eitc/without_children/phase_out/start.yaml)
  - [% Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/dc/tax/income/credits/eitc/with_children/match.yaml) 
  - [Age Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/ma/tax/income/exemptions/aged/age.yaml)


- [List parameter Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/sc/tax/income/subtractions/subtractions.yaml)
- [Marginal rate Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/ny/tax/income/main/joint.yaml)
- [Single amount Example](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/or/tax/income/subtractions/federal_tax_liability/cap/joint.yaml)
- Breakdown parameter
  - Breakdown by Enum variable
  - [Filing status variable example:](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/household/demographic/tax_unit/filing_status.py) 
  - [Filing status parameter example:](https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/ia/tax/income/alternative_minimum_tax/threshold.yaml)

- Scale Parameter interactions: Documentation
  - scale = parameters(period).some.tax.scale
  - scale.thresholds: list[float]
  - scale.amounts: list[float]
  - scale.rates: list[float]
  - scale.thresholds[-1]: float - final element
  - scale.thresholds[0]: float - first element
- Do not use “name:” metadata
   name: mo_federal_income_tax_deduction_rates
- Generally avoid using single amount parameters when scale parameters can created to summarize the value structure 

### Example of a standard parameter

- Essential components: 
    - description 
    - metadata (unit, label, period, reference-title/href)
    - values

- Multiple references example:
    - https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/parameters/gov/states/or/tax/income/subtractions/federal_tax_liability/cap/joint.yaml 
    - Cite both legal code and tax form if possible

- Description
    - Name of State + name of Program
    - Full sentence including period and active language
    - No numeric values
    - Examples:
        - Arizona taxes the personal income for head of household filers at this rate.
        - Rhode Island provides filers a standard deduction of this amount, depending on filing status.
        - New Jersey TANF counts these income sources as unearned income.
        - California limits the young child tax credit to filers with children below this age.
- Label
    - Key Words, no numeric values
    - Not full sentence
    - Name of State + Name of Program
        - Utah income tax rate
        - Iowa nonrefundable tax credits
- Reference 
    - Title: Refer to the specific part of legislative source, as specific as possible
        - Code of the District of Columbia § 47–1806.04 (f)(1)(C)(ii)
        - 2021 DC Form D-40 Booklet, Page 24, Line 5
    - href: the link to the reference. 
        - when applicable, add “# page=page number” to the end of the link to skip to the designated page.
        - Example: https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=24

- Important: economy and household metadata
    - Certain yaml file names are reserved for functions and can not be used 
        - children.yaml
        - if.yaml 
        - parents.yaml
        - else.yaml
    - Set these to false while your program is in development
        - This hides parameters and folders when both are flagged, or if just one is flagged, ensures that users see a notice about the limitations of the parameter:
    - Set them to true when you complete the development and hook it up to the net income tree
    - You can do this at the folder level - [see this example PR](https://github.com/PolicyEngine/policyengine-us/pull/2583)
