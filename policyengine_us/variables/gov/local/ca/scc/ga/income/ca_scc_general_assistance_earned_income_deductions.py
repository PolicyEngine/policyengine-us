from policyengine_us.model_api import *


class ca_scc_general_assistance_earned_income_deductions(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance earned income deductions"
    defined_for = "is_tax_unit_head_or_spouse"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/01Policy/Policy.htm",
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/09Income/Verification_Income.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.scc.general_assistance.countable_income
        person_level = add(person, period, p.earned_deductions.person_sources)
        # Apportion tax-unit-level federal and state income tax across spouses
        # by each person's share of tax-unit earned income, so both spouses'
        # earnings are reduced proportionally by their involuntary withholding.
        person_earned = add(person, period, p.earned_sources)
        tax_unit_earned = person.tax_unit("tax_unit_earned_income", period)
        share = where(tax_unit_earned > 0, person_earned / tax_unit_earned, 0)
        federal_tax = person.tax_unit("income_tax_before_credits", period) * share
        state_tax = person.tax_unit("state_withheld_income_tax", period) * share
        return person_level + federal_tax + state_tax
