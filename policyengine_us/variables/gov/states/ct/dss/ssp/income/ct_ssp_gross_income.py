from policyengine_us.model_api import *


class ct_ssp_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#4005.05",
    )

    def formula(person, period, parameters):
        # Connecticut treats spouses as financially responsible for each other,
        # so deemed income from an ineligible spouse belongs in the gross-income test.
        return add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_unearned_income",
                "ssi",
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
