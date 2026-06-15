from policyengine_us.model_api import *


class fl_sr_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida School Readiness protective-services eligibility pathway"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.fldoe.org/file/20628/2025-2027CCDFStatePlan.pdf#page=26",
        "https://www.flsenate.gov/Laws/Statutes/2025/1002.81",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    def formula(spm_unit, period, parameters):
        # FFY2025-27 CCDF State Plan s. 2.2.2(f)-(h): a child who receives or needs
        # protective services qualifies for School Readiness, and the Lead Agency
        # waives BOTH the income (s. 2.2.2.g = Yes) and the activity (s. 2.2.2.h =
        # Yes) eligibility requirements; see Fla. Stat. 1002.81(1) ("at-risk
        # child"). The age, asset, residency, and program-effective-date
        # requirements still apply. receives_or_needs_protective_services defaults
        # to false and is unpopulated in survey data, so this has ~no microsim
        # effect -- it corrects individual (e.g. app) calculations.
        person = spm_unit.members
        return spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
