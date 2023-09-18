from policyengine_us.model_api import *


class ar_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas dependent personal credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        us_dependent = tax_unit("tax_unit_dependents", period)
        person = tax_unit.members
        p_ar = parameters(
            period
        ).gov.states.ar.tax.income.credits.personal.amount

        is_disabled = person("is_disabled", period)
        is_dependent = person("is_tax_unit_dependent", period)
        disabled_dependent = is_disabled & is_dependent
        count_disabled_dependent = tax_unit.sum(disabled_dependent)
    
        return us_dependent * p_ar.dependent + count_disabled_dependent * p_ar.disabled_dependent
