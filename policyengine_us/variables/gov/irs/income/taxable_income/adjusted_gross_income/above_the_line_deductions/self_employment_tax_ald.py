from policyengine_us.model_api import *


class self_employment_tax_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employment tax ALD deduction"
    unit = USD
    documentation = (
        "Above-the-line deduction for the deductible part of the head's and "
        "spouse's self-employment tax (Schedule 1, line 15). A tax unit "
        "dependent figures their own self-employment tax on their own "
        "Schedule SE and deducts its deductible part on their own return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/164#f",
        "https://www.irs.gov/pub/irs-prior/f1040sse--2025.pdf",
    )

    def formula(tax_unit, period, parameters):
        # A dependent's self-employment income is left off this return by
        # irs_gross_income, so the deduction for their tax is left off too.
        return tax_unit_non_dep_sum("self_employment_tax_ald_person", tax_unit, period)
