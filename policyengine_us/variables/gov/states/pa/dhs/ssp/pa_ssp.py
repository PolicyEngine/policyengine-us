from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class pa_ssp(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/s299.1.html",
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/s299.36.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#k",
        "http://services.dpw.state.pa.us/oimpolicymanuals/ltc/450_Income/450_2_Countable_Income.htm#450.243_SSI_Benefits",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ssp
        arrangement = person("pa_ssp_living_arrangement", period)
        arrangements = arrangement.possible_values
        care = (arrangement == arrangements.DOMICILIARY_CARE) | (
            arrangement == arrangements.PERSONAL_CARE
        )
        individual = p.amount.individual[arrangement]
        couple = p.amount.couple[arrangement]
        payment = ssi_state_supplement(
            person, period, parameters, individual, couple, federal_payment_rules=care
        )
        age = person("age", period.this_year)
        payment = where(care & (age < p.care_age_threshold), 0, payment)
        # LTC Handbook 450.243: SSI recipients in a Medicaid facility get the
        # state-issued Supplement for Personal Needs, so federal rounding and
        # the federal minimum payment do not apply.
        medical = arrangement == arrangements.MEDICAID_INSTITUTION
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        return where(medical, receives_ssi * individual, payment)
