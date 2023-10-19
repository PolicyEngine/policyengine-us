from policyengine_us.model_api import *


class ar_perosnal_credit_aged_special_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas eligibility ofr aged special personal credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        us_aged = person("age", period)
        p = parameters(period).gov.states.ar.tax.income.credits.personal
        aged_thres = p.aged.age_threshold
        is_aged = us_aged >= aged_thres

        does_receive_exemption = (
            person(
                "ar_retirement_or_disability_benefits_exemptions_indv", period
            )
            == 0
        )
        aged_special = is_aged & does_receive_exemption
        return aged_special
