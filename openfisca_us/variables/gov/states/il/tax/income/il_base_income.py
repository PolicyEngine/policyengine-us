from openfisca_us.model_api import *


class il_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        person = tax_unit.members

        federal_agi = tax_unit("adjusted_gross_income", period)
        federal_tax_exempt_interest = sum(
            person("tax_exempt_interest_income", period)
        )
        dividend_income = sum(person("dividend_income", period))
        social_security_benefits = sum(person("social_security", period))

        schedule_m_additions = tax_unit("il_schedule_m_additions", period)
        schedule_m_subtractions = tax_unit("il_schedule_m_subtractions", period)

        # TODO: add Illinois Income Tax overpayment, and other adjustments

        return (
            federal_agi
            + federal_tax_exempt_interest
            + dividend_income
            + schedule_m_additions
            - social_security_benefits
            - schedule_m_subtractions
        )
