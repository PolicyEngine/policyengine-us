from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Nebraska Child Care Subsidy program eligible"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://dhhs.ne.gov/Pages/Child-Care-Parents.aspx",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs
        income = tax_unit("adjusted_gross_income", period)
        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.fpg_fraction
        return income <= income_limit
