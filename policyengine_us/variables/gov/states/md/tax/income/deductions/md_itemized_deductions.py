from policyengine_us.model_api import *


class md_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=5"
        "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=5"
    )
    defined_for = StateCode.MD
    adds = ["itemized_deductions_less_salt", "capped_property_taxes"]
