from policyengine_us.model_api import *


class ca_tanf_applicant_financial_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Applicant Financial Test"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        # AB 74 (2013), section 38(a), amending WIC 11450.12(a).
        "https://www.leginfo.ca.gov/pub/13-14/bill/asm/ab_0051-0100/ab_74_bill_20130627_chaptered.html",
        # MPP 44-207.11.
        "https://cdss.ca.gov/ord/entres/getinfo/pdf/11EAS.pdf#page=11",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2021/21-130.pdf?ver=2021-12-03-084106-333#page=3",
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/income/earned-income-disregards.html",
    )

    def formula(spm_unit, period, parameters):
        countable_income_applicant = spm_unit(
            "ca_tanf_countable_income_applicant", period
        )
        income_limit = spm_unit("ca_tanf_income_limit", period)

        return countable_income_applicant < income_limit
