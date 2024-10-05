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
        # The disability_benefits variable includes only taxable disability benefits.
        disability_benefits = person("disability_benefits", period)
        capped_disability_benefits = min_(disability_benefits, p.cap)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_disablity_exemption = (
            capped_disability_benefits * is_head_or_spouse
        )
        # People who reveive the blind exemption are not eligible for
        # the disability income exemption
        blind_exemption_received = person(
            "la_receives_blind_exemption", period
        )
        return where(blind_exemption_received, 0, total_disablity_exemption)
