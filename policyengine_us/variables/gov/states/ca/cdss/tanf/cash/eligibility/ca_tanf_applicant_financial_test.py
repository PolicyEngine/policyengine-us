from policyengine_us.model_api import *


class ca_tanf_applicant_financial_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Applicant Financial Test"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/income/earned-income-disregards.html"

    def formula(spm_unit, period, parameters):
        countable_income_applicant = spm_unit(
            "ca_tanf_countable_income_applicant", period
        )
        income_limit = spm_unit("ca_tanf_income_limit", period)

        return countable_income_applicant <= income_limit
