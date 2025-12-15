from policyengine_us.model_api import *


class mn_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the Minnesota child and dependent care expense credit"
    )
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        if p.separate_filers_excluded:
            filing_status = tax_unit("filing_status", period)
            return filing_status != filing_status.possible_values.SEPARATE
        else:
            return True
