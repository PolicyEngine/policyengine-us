"""
Connecticut TFA gross unearned income calculation.
"""

from policyengine_us.model_api import *


class ct_tfa_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA gross unearned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Total gross unearned income for the Connecticut TFA assistance unit, "
        "including unemployment compensation, Social Security benefits (excluding SSI), "
        "and other unearned income sources before any exclusions."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Treatment Section; "
        "Connecticut DSS Uniform Policy Manual Section 8030"
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Unearned income sources (SSI is specifically excluded)
        unemployment_compensation = person("unemployment_compensation", period)
        social_security = person("social_security", period)

        # Other unearned income sources
        dividend_income = person("dividend_income", period)
        interest_income = person("taxable_interest_income", period)
        pension_income = person("pension_income", period)
        rental_income = person("rental_income", period)

        # Total unearned income per person
        total_unearned = (
            unemployment_compensation
            + social_security
            + dividend_income
            + interest_income
            + pension_income
            + rental_income
        )

        # Sum across household
        return spm_unit.sum(total_unearned)
