from policyengine_us.model_api import *


class la_disability_income_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Louisiana disability income exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"  # (B)
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.income.exempt_income.disability
        # All disability benefits are exempt from income tax
        disability_benefits = person("disability_benefits", period)
        capped_disability_benefits = min_(disability_benefits, p.cap)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return capped_disability_benefits * is_head_or_spouse
