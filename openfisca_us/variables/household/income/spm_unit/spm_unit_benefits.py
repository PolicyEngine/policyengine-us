from openfisca_us.model_api import *


class spm_unit_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "Benefits"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        BENEFITS = [
            "social_security",
            "ssi",
            "ca_cvrp",  # California Clean Vehicle Rebate Project.
            "snap",
            "wic",
            "free_school_meals",
            "reduced_price_school_meals",
            "lifeline",
            "acp",
            "ebb",
            "spm_unit_capped_housing_subsidy",
            "tanf",
            "high_efficiency_electric_home_rebate",
            "residential_efficiency_electrification_rebate",
            # Contributed.
            "basic_income",
        ]
        if parameters(period).contrib.ubi_center.flat_tax.deduct_ptc:
            BENEFITS.append("premium_tax_credit")
        return add(spm_unit, period, BENEFITS)
