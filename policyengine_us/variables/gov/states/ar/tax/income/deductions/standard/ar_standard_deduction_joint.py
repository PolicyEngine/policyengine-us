from policyengine_us.model_api import *


class ar_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas standard deduction when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/2003/Public/ACT997.pdf#page=1",
        "https://arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/2013/Public/ACT1488.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions
        filing_status = person.tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        # Arkansas grants each taxpayer and spouse a deduction in 26-51-430.
        # DFA says the deduction does not apply to dependents.
        # Keep each filer's entitlement rather than the instructions' restriction.
        return is_head * p.standard[filing_status]
