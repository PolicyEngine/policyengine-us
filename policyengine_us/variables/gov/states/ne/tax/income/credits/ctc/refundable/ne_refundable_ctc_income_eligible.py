from policyengine_us.model_api import *


class ne_refundable_ctc_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit total household income eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.fpg_fraction
        # Total household income is defined as federal adjusted gross income
        # as per Nebraska Department of Revenue
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        return adjusted_gross_income <= income_limit
