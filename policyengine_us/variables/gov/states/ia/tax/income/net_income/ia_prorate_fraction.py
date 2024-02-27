from policyengine_us.model_api import *


class ia_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Iowa joint amount proration fraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        net_income = person("ia_net_income", period)
        total_net_income = person.tax_unit.sum(net_income)
        # avoid divide-by-zero warnings when using where() function
        fraction = np.zeros_like(total_net_income)
        mask = total_net_income != 0
        fraction[mask] = net_income[mask] / total_net_income[mask]
        # if no net income, then assign entirely to head.
        return where(
            total_net_income == 0,
            person("is_tax_unit_head", period),
            fraction,
        )
