from policyengine_us.model_api import *


class nv_oss_payment_standard(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Nevada OSS maximum monthly payment per person"
    defined_for = StateCode.NV
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#i",
        "https://secure.ssa.gov/poms.nsf/lnx/0502005030#G",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nv.dwss.oss.payment
        arrangement = person("nv_oss_living_arrangement", period)
        category = person("ssi_category", period.this_year)
        couple = person("ssi_couple_computation_applies", period)
        # Half of each member's same-category couple rate reproduces all
        # mixed-category totals in SI 01415.058 I.2.b. SI 02005.030 G.1
        # divides the joint payment equally, including aged/disabled couples.
        couple_total = person.marital_unit.sum(p.couple[arrangement][category] / 2)
        return where(couple, couple_total / 2, p.individual[arrangement][category])
