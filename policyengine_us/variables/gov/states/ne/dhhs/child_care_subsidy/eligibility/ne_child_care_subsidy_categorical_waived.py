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
        # 392 NAC 2-011.02 through 2-011.03 grant eligibility without regard
        # to income to parents and foster parents of Department or tribal
        # wards, and 392 NAC 1-001.32 defines the category as families
        # requiring Child Protective Services. State Plan question 2.2.2(f)
        # counts foster-care and court-supervised children as protective
        # services, and questions 2.2.2(g) and 2.2.6(b) waive the income and
        # asset tests for them. Question 2.2.6(b) also extends the waiver to
        # subsidized guardianship and adoption families, which the model
        # cannot separately identify, so they are not modeled.
        protective = person("receives_or_needs_protective_services", period.this_year)
        return spm_unit.sum(foster | protective) > 0
