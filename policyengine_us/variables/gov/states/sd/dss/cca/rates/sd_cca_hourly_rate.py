from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.sd.dss.cca.rates.sd_cca_provider_type import (
    SDCCAProviderType,
)


class sd_cca_hourly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "South Dakota CCA hourly maximum reimbursement rate per child"
    documentation = "Computes the hourly ceiling from the July 2024 county rate sheets, including approved special-needs care and qualified specialized infant and toddler care."
    definition_period = MONTH
    defined_for = "sd_cca_eligible_child"
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Family_Child_Care.pdf",
        "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Center_Care.pdf",
        "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Before_After_School_Programs.pdf",
        "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Relative_In-Home_and_Informal_Care.pdf",
    )

    def formula_2024_07_01(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.rates.hourly
        county = person.household("county_str", period.this_year)
        county = where(np.isin(county, p.counties), county, "UNKNOWN")
        age = person("age", period.this_year)
        # DSS uses three age bands in the hourly sheets. School enrollment
        # does not move a five-year-old into the six-and-over band.
        age_group = select(
            [
                age < p.age_group.infant_toddler_age_limit,
                age < p.age_group.preschool_age_limit,
            ],
            ["UNDER_THREE", "THREE_TO_FIVE"],
            default="SIX_AND_OVER",
        )
        provider_type = person("sd_cca_provider_type", period)
        family_rate = p.family_day_care[county][age_group]
        specialized = person("sd_cca_specialized_infant_toddler_rate_eligible", period)
        family_rate = family_rate * where(
            specialized & (age < p.age_group.infant_toddler_age_limit),
            p.specialized_infant_toddler_multiplier,
            1,
        )
        center_rate = p.licensed_center[county][age_group]
        base_rate = select(
            [
                provider_type == SDCCAProviderType.FAMILY_DAY_CARE,
                provider_type == SDCCAProviderType.INFORMAL,
                provider_type == SDCCAProviderType.BEFORE_AFTER_SCHOOL,
            ],
            [family_rate, p.informal, p.before_after_school[county]],
            default=center_rate,
        )
        # DSS approves enhanced services separately from disability status.
        # The published special-needs ceiling replaces the ordinary ceiling;
        # it does not multiply the specialized infant and toddler rate.
        approved = person("sd_cca_special_needs_rate_approved", period)
        return where(approved, p.special_needs_maximum, base_rate)
