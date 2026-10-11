from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.category.msp_category import (
    MSPCategory,
)


class qmb_cost_sharing(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Qualified Medicare Beneficiary cost-sharing value"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396d#p_3",
        "https://www.law.cornell.edu/uscode/text/42/1396a#n_2",
    )
    documentation = (
        "Monthly Medicaid spending on Medicare deductibles, coinsurance, and "
        "copayments for a Qualified Medicare Beneficiary. The model lacks "
        "Medicare claims, so this is national Medicaid spending on Medicare "
        "cost sharing for Qualified Medicare Beneficiaries per enrollee, from "
        "CMS-64 line 17D, a twelfth each month. 42 U.S.C. 1396a(n)(2) does not "
        "require a state to pay cost sharing once Medicare's payment reaches "
        "the state's Medicaid rate, and most states limit payment this way, so "
        "this spending is below the cost sharing Medicare charges."
    )

    def formula(person, period, parameters):
        category = person("msp_category", period)
        per_enrollee = parameters(
            period
        ).calibration.gov.hhs.medicare.savings_programs.qmb_cost_sharing_per_enrollee
        return (category == MSPCategory.QMB) * per_enrollee / MONTHS_IN_YEAR
