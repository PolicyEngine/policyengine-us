from policyengine_us.model_api import *


class id_retirement_benefits_deduction_relevant_income(Variable):
    value_type = float
    entity = Person
    label = "Idaho retirement benefits deduction income sources"
    documentation = """
    The person's retirement benefits that count toward the Idaho retirement
    benefits deduction (Form 39R line 8e): the benefits in Idaho Code
    63-3022A(1)(a) if the person meets that paragraph's age test, and
    military retirement benefits if the person meets the test of
    63-3022A(1)(b).
    """
    unit = USD
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
    )
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.deductions.retirement_benefits
        general_benefits = add(person, period, p.income_sources)
        general_eligible = person(
            "id_retirement_benefits_deduction_eligible_person", period
        )
        military_benefits = person("id_eligible_military_retirement_income", period)
        military_eligible = person(
            "id_retirement_benefits_deduction_military_eligible_person", period
        )
        return (
            general_benefits * general_eligible + military_benefits * military_eligible
        )
