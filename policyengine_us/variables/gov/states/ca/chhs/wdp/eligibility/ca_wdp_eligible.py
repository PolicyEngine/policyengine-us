from policyengine_us.model_api import *


class ca_wdp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program eligible"
    definition_period = YEAR
    documentation = (
        "Eligibility for California's 250% Working Disabled Program. The model "
        "covers disability status without an SGA screen, paid work, net family "
        "income below 250% FPL, a first-pass SSI/SSP income screen without "
        "earnings, SSI/SSP immigration status, and current and historical asset "
        "limits. County enrollment verification, full SSI/SSP deeming, and "
        "temporary unemployment continuation are not modeled."
    )
    reference = (
        "https://www.dhcs.ca.gov/services/working-disabled-program/",
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/medi-cal/non-magi/250-percent-wdp.html",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return (
            person("ca_wdp_disability_eligible", period)
            & person("ca_wdp_work_eligible", period)
            & person("ca_wdp_income_eligible", period)
            & person("ca_wdp_ssi_ssp_income_eligible", period)
            & person("ca_wdp_immigration_status_eligible", period)
            & person("ca_wdp_asset_eligible", period)
        )
