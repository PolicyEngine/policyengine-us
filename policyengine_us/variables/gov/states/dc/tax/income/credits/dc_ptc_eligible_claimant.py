from policyengine_us.model_api import *


class dc_ptc_eligible_claimant(Variable):
    value_type = bool
    entity = Person
    label = "Person can claim the DC property tax credit"
    definition_period = YEAR
    reference = (
        # D.C. Code 47-1806.06(b)(4) and (k).
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.06",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1801.04#(13)",
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ptc
        filer = person("is_tax_unit_head_or_spouse", period)
        # The federal filing exception permits claiming one's own dependents;
        # it does not remove dependent status under section 152.
        dependent = person("claimable_as_dependent_on_another_return", period)
        old_enough = person("age", period) >= p.dependent_claimant_min_age
        return filer & (~dependent | old_enough)
