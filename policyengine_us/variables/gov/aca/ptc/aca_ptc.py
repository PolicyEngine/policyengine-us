from policyengine_us.model_api import *


class aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA premium tax credit for tax unit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"
    documentation = (
        "The premium tax credit from 2014 onward, subject to filing a return. "
        "For 2014 through 2017, benchmark premiums use 2018 rating-area "
        "premiums scaled by the national benchmark premium index."
    )
    defined_for = "is_aca_ptc_eligible"

    def formula(tax_unit, period, parameters):
        return 0

    def formula_2014(tax_unit, period, parameters):
        # IRC § 36B(a) conditions the PTC on filing a return (Form 8962), so
        # a tax unit that neither files nor takes up the credit receives $0.
        # Taking up the credit means filing to claim or reconcile it.
        credit = tax_unit("aca_ptc_before_filing_gate", period)
        files = tax_unit("files_return_for_aca_ptc", period)
        return credit * files
