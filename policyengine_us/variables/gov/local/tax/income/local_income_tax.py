from policyengine_us.model_api import *


class local_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax"
    documentation = "Local income, wage, and earnings taxes."
    unit = USD

    # This SALT-deductible measure excludes the Yonkers tax: the Yonkers
    # resident surcharge is a fraction of NY State tax, which depends on the
    # federal SALT deduction, so including it here would create a circular
    # dependency. Yonkers is still levied via
    # local_income_tax_before_refundable_credits.
    adds = [
        "nyc_income_tax",
        "pa_philadelphia_wage_tax",
        "mo_kansas_city_earnings_tax",
        "mo_st_louis_earnings_tax",
        "de_wilmington_earned_income_tax",
    ]
