from policyengine_us.model_api import *


class ne_child_care_subsidy_categorical_waived(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy income and asset tests waived"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=19",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=14",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        foster = person("is_in_foster_care", period)
        # 392 NAC 2-011.02-.03 concerns Department/tribal wards. The Plan's
        # 2.2.2(f)-(g) includes families under court supervision in protective
        # services and permits case-by-case income waivers. An individual's
        # supervision alone does not establish that family/case status; use
        # the separate protective-services input for a qualifying case.
        # 2.2.6(b)'s asset-waiver narrative and 3.3.1(vi)'s fee waiver are
        # narrower (wards, subsidized adoption/guardianship). The existing
        # shared protective-services approximation is retained, not expanded.
        protective = person("receives_or_needs_protective_services", period.this_year)
        return spm_unit.sum(foster | protective) > 0
