from policyengine_us.model_api import *
from policyengine_us.tools.general import has_input_for_period


class ca_capi_countable_for_snap(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "California CAPI countable as SNAP unearned income"
    unit = USD
    defined_for = StateCode.CA
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(b)(2)(i)",
        "https://stgenssa.sccgov.org/debs/program_handbooks/calfresh/assets/CalFresh/Income_Definitions_and_Exemptions/Unearned.htm",
    )

    def formula(person, period):
        # An explicitly supplied unit grant replaces the calculated person
        # amounts and is counted separately as unit income.
        if has_input_for_period(person.simulation, "ca_capi", period.this_year):
            return 0
        # The CAPI person amount is calculated before the unit resource test.
        # Apply the same unit eligibility gate as the paid CAPI benefit.
        eligible = person.spm_unit("ca_capi_eligible", period.this_year)
        potential_payment = person("ca_capi_person", period)
        return where(eligible, potential_payment, 0)
