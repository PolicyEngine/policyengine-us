from policyengine_us.model_api import *


class heating_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Heating cost for each person"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        total = add(
            spm_unit,
            period,
            [
                "electricity_expense",
                "gas_expense",
                "fuel_oil_expense",
                "heating_cooling_expense",
            ],
        )
        spm_size = spm_unit.nb_persons()
        per_person = np.zeros_like(total)
        mask = spm_size > 0
        per_person[mask] = total[mask] / spm_size[mask]
        return spm_unit.project(per_person)
