from policyengine_us.model_api import *


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored."
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"

    def formula(tax_unit, period, parameters):
        # set up simulation clone
        simulation = tax_unit.simulation
        simulation.max_spiral_loops = 10
        simulation._check_for_cycle = lambda *args: None
        EITC_VARIABLES = [
            "eitc_agi_limit",
            "eitc_child_count",
            "eitc_eligible",
            "eitc_demographic_eligible",
            "eitc_investment_income_eligible",
            "eitc_maximum",
            "eitc_phased_in",
            "eitc_reduction",
            "eitc",
        ]
        for variable in EITC_VARIABLES:
            simulation.get_holder(variable).delete_arrays()

        # modify EITC minimum age condition in simulation clone
        tbs = simulation.tax_benefit_system
        original_age = tbs.parameters.gov.irs.credits.eitc.eligibility.age.min(
            period
        )
        tbs.parameters.gov.irs.credits.eitc.eligibility.age.min.update(
            value=0,
            period=period,
        )
        tbs.parameters.gov.irs.credits.eitc._at_instant_cache = {}
        eitc = simulation.calculate("eitc", period)
        for variable in EITC_VARIABLES:
            simulation.get_holder(variable).delete_arrays()
        tbs.parameters.gov.irs.credits.eitc.eligibility.age.min.update(
            value=original_age,
            period=period,
        )
        tbs.parameters.gov.irs.credits.eitc._at_instant_cache = {}
        return eitc
