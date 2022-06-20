from openfisca_us.model_api import *


class meets_wic_categorical_eligibility(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = (
        "Meets the program participation eligibility criteria for WIC"
    )
    label = "Meets WIC categorical (program participation) eligibility"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A"

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_ii
        receives_snap_or_tanf = add(spm_unit, period, ["snap", "tanf"]) > 0
        # https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_iii
        receives_medicaid = person("medicaid", period) > 0
        # "is a member of a family in which a pregnant woman or an infant receives [Medicaid]."
        pregnant = person("is_pregnant", period)
        wic_category = person("wic_category", period)
        infant = wic_category == wic_category.possible_values.INFANT
        pregnant_or_infant_medicaid_in_spmu = spm_unit.any(
            receives_medicaid & (pregnant | infant)
        )
        return (
            receives_snap_or_tanf
            | receives_medicaid
            | pregnant_or_infant_medicaid_in_spmu
        )
