from policyengine_us.model_api import *


class rent(Variable):
    value_type = float
    entity = Person
    label = "Rent"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        pre_subsidy_rent = person("pre_subsidy_rent", period)
        total_pre_subsidy_rent = person.spm_unit.sum(pre_subsidy_rent)
        housing_subsidy = person.spm_unit("housing_assistance", period)
        rent_fraction = np.zeros_like(total_pre_subsidy_rent)
        mask = total_pre_subsidy_rent != 0
        rent_fraction[mask] = (
            pre_subsidy_rent[mask] / total_pre_subsidy_rent[mask]
        )
        subsidy_fraction = rent_fraction * housing_subsidy
        return max_(pre_subsidy_rent - subsidy_fraction, 0)
