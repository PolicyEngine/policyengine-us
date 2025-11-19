## Variables

- Variable structure
    - Determing value type, entity [TBD]
    - Ensure the naming aligns with variable file name
    - Refer to existing variables with similar structure

See Examples below: 

```
#Example-1
from policyengine_us.model_api import *

class ca_additions(Variable): 
    value_type = float
    entity = TaxUnit
    label = "CA AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    defined_for = StateCode.CA

#Example-2
from policyengine_us.model_api import *

class ca_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Use Tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=22"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        income = tax_unit("ca_agi", period)
        p = parameters(period).gov.states.ca.tax.income.use_tax
        # Compute main amount, a dollar amount based on CA AGI.
        main_amount = p.main.calc(income)
        # Switches to a percentage of income above the top main threshold.
        additional_amount = p.additional.calc(income) * income
        return main_amount + additional_amount
```

- Add readme.md files to state program variable folders per [this PR](https://github.com/PolicyEngine/policyengine-us/pull/2740)
    - Eliminate abbreviations on the front end

- Dividing by 0 Problem
    - [PR example](https://github.com/PolicyEngine/policyengine-us/pull/2561/files) to overcome /0 
    - Mask example:
        - Use when a division can lead to a “dividing by 0” issue
