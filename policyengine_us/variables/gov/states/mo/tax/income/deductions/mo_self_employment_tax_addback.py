from policyengine_us.model_api import *


class mo_self_employment_tax_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri itemized deduction for self-employment tax"
    unit = USD
    documentation = (
        "Self-employment tax added to Missouri itemized deductions, net of the "
        "part already deducted in computing federal adjusted gross income."
    )
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.141",
        # PDF page 42: Form MO-A Part 2 line 7.
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2017.pdf#page=42",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # RSMo 143.141(4)(c): Missouri allows the tax only to the extent the
        # filer didn't deduct it in computing federal AGI.
        self_employment_tax = add(tax_unit, period, ["self_employment_tax"])
        deducted = tax_unit("self_employment_tax_ald", period)
        return max_(0, self_employment_tax - deducted)
