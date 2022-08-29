from openfisca_us.model_api import *


class residential_efficiency_and_electrification_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Residential efficiency and electrification rebate"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.doe.residential_efficiendy_and_electrification_rebate
        expenditures = tax_unit("residential_efficiency_and_electrification_retrofit_expenditures", period)
        savings = tax_unit("residential_efficiency_and_electrification_retrofit_energy_savings", period)
        income_ami = tax_unit("tax_unit_income_ami_ratio", period)
        high_cap = p.amount.cap.high.calc(income_ami)
        medium_cap = p.amount.cap.medium.calc(income_ami)
        percent = p.amount.percent.calc(income_ami)
        uncapped = percent * expenditures
        cap = select([savings >= p.threshold.high, savings >= p.threshold.medium, savings >= p.threshold.low],
        [high_cap, medium_cap, 0], default = 0)
        return min_(uncapped, cap)
