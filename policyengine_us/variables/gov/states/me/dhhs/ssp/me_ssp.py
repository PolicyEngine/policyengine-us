from policyengine_us.model_api import *


class me_ssp(Variable):
    value_type = float
    entity = Person
    label = "Maine State Supplemental Income Program"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
        "https://legislature.maine.gov/statutes/22/title22sec3271.html",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/me.html",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("me_ssp_eligible", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        arrangement = person("me_ssp_living_arrangement", period)
        values = arrangement.possible_values
        marital_unit_size = person.marital_unit.nb_persons()
        # Both spouses must share the same living arrangement to be
        # treated as a joint couple claim. New enum values added to
        # MESSPLivingArrangement must be appended to this check.
        shared_arrangement = (
            (
                person.marital_unit.sum(
                    arrangement == values.LIVING_ALONE_OR_WITH_OTHERS
                )
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.HOUSEHOLD_OF_ANOTHER)
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.ADULT_FOSTER_HOME)
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.FLAT_RATE_BOARDING_HOME)
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.ADULT_FAMILY_CARE_HOME)
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(
                    arrangement == values.COST_REIMBURSED_BOARDING_HOME
                )
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.MEDICAID_FACILITY)
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(arrangement == values.RESIDENTIAL_CARE_FACILITY)
                == marital_unit_size
            )
        )
        couple_applies = joint_claim & both_eligible & shared_arrangement
        return where(
            couple_applies,
            person("me_ssp_couple", period),
            person("me_ssp_individual", period),
        )
