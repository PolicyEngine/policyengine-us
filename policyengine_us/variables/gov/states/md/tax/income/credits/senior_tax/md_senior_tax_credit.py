from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class md_senior_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Senior Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=15"
    )
    defined_for = "md_senior_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.md.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "md_income_tax_before_credits",
            "md_senior_tax_credit",
            "md_senior_tax_credit_potential",
        )
