from policyengine_us.model_api import *


class part_d_lis(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part D low-income subsidy"
    documentation = (
        "Value of the Part D low-income subsidy (Extra Help) as the "
        "Congressional Budget Office counts it: the Medicare Trustees' "
        "average subsidy payment per subsidy enrollee, the same for every "
        "enrollee. Most of the subsidy pays cost sharing, which depends on "
        "each enrollee's drug use, which the model does not have."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114",
        "https://www.cbo.gov/publication/61910",
        "https://www.cbo.gov/system/files/2018-07/54234-workingpaper.pdf#page=46",
        "https://www.cms.gov/oact/tr/2026#page=158",
    )
    defined_for = "part_d_lis_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).calibration.gov.hhs.medicare.part_d
        enrolled = person("part_d_lis_enrolled", period)
        return enrolled * p.low_income_subsidy_per_recipient
