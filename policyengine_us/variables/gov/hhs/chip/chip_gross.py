from policyengine_us.model_api import *


class chip_gross(Variable):
    value_type = float
    entity = Person
    label = "Gross CHIP benefit value"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.macpac.gov/publication/chip-spending-by-state/",
        "https://www.medicaid.gov/medicaid/financial-management/state-expenditure-reporting-for-medicaid-chip/expenditure-reports-mbescbes",
    )
    documentation = (
        "Gross CHIP service value for a CHIP-eligible person, equal to the "
        "per-capita net CHIP spending plus the state's household cost-sharing "
        "offsets. Counterpart to `chip`, which is the net-of-premium value "
        "reported by MACPAC. Use this for household-side resource accounting "
        "when premiums paid by the household are tracked separately via "
        "`chip_premium`."
    )
    defined_for = "is_chip_eligible"
    adds = ["per_capita_chip_gross"]
