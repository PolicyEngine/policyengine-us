from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ia_ssa_has_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA spouse living with the person"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/3987/download?inline=#page=12",
        "https://www.ecfr.gov/current/title-20/section-416.1806",
    )

    def formula(person, period, parameters):
        # 6-B Resources p.12: "When the applicant is living with a spouse,
        # count the spouse's resources." SSI's spouse lookup also identifies
        # the actual couple in a default marital unit with unrelated adults,
        # and excludes a parent and the adult child they claim as a dependent.
        return _ssi_spouse_index(person, period.this_year) >= 0
