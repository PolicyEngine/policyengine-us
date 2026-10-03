from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class nh_fap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP income limit"
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=17, 74"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap
        size = spm_unit("nh_fap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        household_smi = smi(size, state, period, parameters)
        # Numerical inference matching all eight PY2027 published amounts:
        # floor the four-person limit, apply the federal factor, then floor.
        # The manual does not prescribe that intermediate rounding order.
        four_person_limit = np.floor(four_person_smi * p.smi_rate)
        # Federal factors are integer percentages; recover them to avoid a
        # floating-point value just below an exact whole-dollar boundary.
        factor_percent = np.rint(household_smi / four_person_smi * 100)
        limit = np.floor(four_person_limit * factor_percent / 100)
        # Federal size extensions are retained; NH rounding above eight is
        # unverified. A household with no qualified member is ineligible.
        return where(size > 0, limit, 0)
