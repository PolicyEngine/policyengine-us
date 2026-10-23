from policyengine_us.model_api import *


class ar_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR3_ItemizedDeduction.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2021_AR1000F_and_AR1000NR_Instructions.pdf#page=20",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Arkansas does not tie itemization choice to federal choice.
        deductions = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.sources.joint
        unit_deds = add(person.tax_unit, period, deductions)
        # Arkansas freezes IRC 163 as of January 1, 2017, when the premium
        # deduction had expired after 2016 (AR3 interest lines 8-10).
        disallowed_interest = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.disallowed_interest_components
        if disallowed_interest:
            unit_deds = unit_deds - add(person.tax_unit, period, disallowed_interest)
        is_head = person("is_tax_unit_head", period)
        return unit_deds * is_head
