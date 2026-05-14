from policyengine_us.model_api import *


class ga_ssp_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Georgia State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/medicaid/2578/",
        "https://pamms.dhs.ga.gov/dfcs/medicaid/2136/",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
    )

    def formula(person, period, parameters):
        arrangement = person("ssi_federal_living_arrangement", period.this_year)
        in_federal_medicaid_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        in_georgia_ssp_setting = person(
            "ga_ssp_in_nursing_home_or_institutionalized_hospice",
            period.this_year,
        )
        ssi_amount = person("ssi", period)
        # in_federal_medicaid_facility already confirms MEDICAL_TREATMENT_FACILITY
        # arrangement, so any positive SSI confirms institutional SSI receipt.
        receives_institutional_ssi = ssi_amount > 0
        return (
            receives_institutional_ssi
            & in_federal_medicaid_facility
            & in_georgia_ssp_setting
        )
