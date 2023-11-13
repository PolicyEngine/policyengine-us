from policyengine_us.model_api import *


class ar_personal_credit_aged_special(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas aged special personal credit"
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.credits.personal.aged
        total_aged_special_people = add(
            tax_unit, period, ["ar_personal_credit_aged_special_eligible"]
        )

        return total_aged_special_people * (p.special + p.base)
