from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted gross income for the West Virginia low-income family tax credit"
    unit = USD
    definition_period = YEAR
    # W. Va. Code 11-21-22a(d): "the federal adjusted gross income plus any
    # applicable increasing West Virginia modifications plus any tax exempt
    # interest income reported on the federal tax return".
    reference = "https://code.wvlegislature.gov/11-21-22a/"
    defined_for = "wv_low_income_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        # The tax-exempt interest is the head's and spouse's, reported on
        # their federal return; a tax unit dependent's is on the dependent's
        # own return, as federal adjusted gross income leaves it out.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            ["adjusted_gross_income", "tax_exempt_interest_income", "wv_additions"],
        )
