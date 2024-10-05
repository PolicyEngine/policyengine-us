from policyengine_us.model_api import *


class ar_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR3_ItemizedDeduction.pdf"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Arkansas does not tie itemization choice to federal choice.
        deductions = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.sources.joint
        unit_deds = add(person.tax_unit, period, deductions)
        is_head = person("is_tax_unit_head", period)
        return unit_deds * is_head
