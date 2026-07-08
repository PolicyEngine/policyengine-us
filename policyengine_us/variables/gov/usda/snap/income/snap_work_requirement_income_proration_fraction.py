from policyengine_us.model_api import *


class snap_work_requirement_income_proration_fraction(Variable):
    value_type = float
    entity = Person
    label = "SNAP work requirement income proration fraction"
    definition_period = MONTH
    documentation = "Under 7 CFR 273.11(c)(2), the income of ABAWD time-limit ineligible members is prorated among remaining household members, while 7 CFR 273.11(c)(1) counts work-sanctioned members' income in full. The model applies proration to all work-requirement-ineligible members as a simplification; in the baseline only ABAWD time-limit failures occur, so proration is the applicable rule."
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_2"

    def formula(person, period, parameters):
        meets_work_requirements = person("meets_snap_work_requirements_person", period)
        snap_unit_size = person.spm_unit("snap_unit_size", period)
        unit_size = person.spm_unit("spm_unit_size", period)
        ineligible_fraction = where(unit_size > 0, snap_unit_size / unit_size, 0)
        return where(meets_work_requirements, 1, ineligible_fraction)
