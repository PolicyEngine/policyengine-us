from policyengine_us.model_api import *


class or_tax_before_credits_in_prior_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR tax before credits in prior year"
    unit = USD
    documentation = (
        "Oregon income tax before credits for the prior tax year, the base of "
        "the kicker credit claimed on the current-year return. When not "
        "provided, it defaults to the current year's Oregon income tax before "
        "credits as a proxy for the prior-year liability."
    )
    definition_period = YEAR
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=18"
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # The kicker on an odd-year return is a percentage of the prior year's
        # liability (2025 OR-40 line 32: 9.863% of 2024 liability). Household
        # and microsimulation inputs usually cover a single year, so reading
        # period.last_year would return 0; the current-year liability is used
        # as a proxy instead. An explicit input overrides this formula.
        return tax_unit("or_income_tax_before_credits", period)
