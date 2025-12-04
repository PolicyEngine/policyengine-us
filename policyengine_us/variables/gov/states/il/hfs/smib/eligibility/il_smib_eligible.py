from policyengine_us.model_api import *


class il_smib_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois SMIB Buy-In Program eligible"
    definition_period = MONTH
    documentation = (
        "Eligible for Illinois Supplementary Medical Insurance Benefit "
        "(SMIB) Buy-In Program. The program pays Medicare Part B premiums "
        "for eligible individuals receiving AABD, TANF, SSI, or who qualify "
        "as QMB/SLMB/QI under the Medicare Savings Program."
    )
    reference = (
        "https://www.ilga.gov/commission/jcar/admincode/089/089001200D00700R.html",
        "https://www.dhs.state.il.us/page.aspx?item=18685",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Must be Medicare eligible (or meet other SMIB criteria)
        is_medicare = person("is_medicare_eligible", period.this_year)
        # Check categorical eligibility (AABD, TANF, SSI)
        categorical_eligible = person("il_smib_categorical_eligible", period)
        # Note: QMB/SLMB/QI eligibility will come from MSP when that PR merges
        # For now, categorical eligibility is the primary path
        return is_medicare & categorical_eligible
