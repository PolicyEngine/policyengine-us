from policyengine_us.model_api import *


class ar_deaf_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas deaf personal credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person=tax_unit.members
        us_deaf = person("is_deaf", period)
        total_deaf = tax_unit.sum(us_deaf)
        p_ar = parameters(
            period
        ).gov.states.ar.tax.income.credits.personal.amount
        return total_deaf * p_ar.deaf
