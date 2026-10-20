from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ia_ssa_has_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA spouse in the marital unit"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/3987/download?inline=#page=12",
        "https://www.ecfr.gov/current/title-20/section-416.1806",
    )

    def formula(person, period, parameters):
        # 6-B Resources p.12: "When the applicant is living with a spouse,
        # count the spouse's resources." A two-person marital unit is a couple
        # only when SSI's spouse test pairs its members, so the default unit of
        # a situation without marital units does not pair a parent with an
        # adult child the parent claims (ia_ssa.yaml Case 79). A default unit
        # of three or more people budgets each member alone.
        couple_unit = person.marital_unit.nb_persons() == 2
        return couple_unit & (_ssi_spouse_index(person, period) >= 0)
