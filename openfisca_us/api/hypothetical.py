import numpy as np
import openfisca_us
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.periods import period

class IndividualSim:
    def __init__(self, *reforms, year=2018):
        self.year = year
        self.reforms = reforms
        self.system = openfisca_us.CountryTaxBenefitSystem()
        self.entities = {var.key: var for var in self.system.entities}
        self.apply_reforms(self.reforms)
        self.situation_data = {"people": {}, "taxunits": {}}
        self.varying = False
        self.num_points = None

    def build(self):
        self.sim_builder = SimulationBuilder()
        self.system = openfisca_us.CountryTaxBenefitSystem()
        self.apply_reforms(self.reforms)
        self.sim = self.sim_builder.build_from_entities(
            self.system, self.situation_data
        )

    def apply_reforms(self, reforms: list) -> None:
        """Applies a list of reforms to the tax-benefit system.

        Args:
            reforms (list): A list of reforms. Each reform can also be a list of reforms.
        """
        for reform in reforms:
            if isinstance(reform, tuple) or isinstance(reform, list):
                self.apply_reforms(reform)
            else:
                self.system = reform(self.system)

    def add_data(
        self,
        entity="people",
        name=None,
        input_period=None,
        auto_period=True,
        **kwargs,
    ):
        input_period = input_period or self.year
        entity_plural = self.entities[entity].plural
        if name is None:
            name = (
                entity + "_" + str(len(self.situation_data[entity_plural]) + 1)
            )
        if auto_period:
            data = {}
            for var, value in kwargs.items():
                try:
                    def_period = self.system.get_variable(
                        var
                    ).definition_period
                    if def_period in ["eternity", "year"]:
                        input_periods = [input_period]
                    else:
                        input_periods = period(input_period).get_subperiods(
                            def_period
                        )
                    data[var] = {
                        str(subperiod): value for subperiod in input_periods
                    }
                except:
                    data[var] = value
        self.situation_data[entity_plural][name] = data
        self.build()

    def add_person(self, **kwargs):
        self.add_data(entity="person", **kwargs)

    def add_taxunit(self, **kwargs):
        self.add_data(entity="taxunit", name="taxunit", **kwargs)

    def get_entity(self, name):
        entity_type = [
            entity
            for entity in self.entities.values()
            if name in self.situation_data[entity.plural]
        ][0]
        return entity_type

    def get_group(self, entity, name):
        containing_entity = [
            group
            for group in self.situation_data[entity.plural]
            if name == self.situation_data[entity.plural][group]["head"]
            or name == self.situation_data[entity.plural][group]["spouse"]
            or name in self.situation_data[entity.plural][group]["dependents"]
        ][0]
        return containing_entity

    def calc(self, var, period=None, target=None, index=None):
        period = period or self.year
        entity = self.sim_builder.get_variable_entity(var)
        if target is not None:
            target_entity = self.get_entity(target)
            if target_entity.key != entity.key:
                target = self.get_group(entity, target)
        try:
            result = self.sim.calculate(var, period)
        except:
            try:
                result = self.sim.calculate_add(var, period)
            except:
                result = self.sim.calculate_divide(var, period)
        if self.varying:
            result = result.reshape(
                (self.num_points, len(self.situation_data[entity.plural]))
            ).transpose()
        members = list(self.situation_data[entity.plural])
        if index is not None:
            index = min(len(members) - 1, index)
        if target is not None:
            index = members.index(target)
        if target is not None or index is not None:
            return result[index]
        return result

    def calc_deriv(
        self,
        var,
        wrt="employment_income",
        period=None,
        var_target=None,
        wrt_target=None,
    ):
        period = period or self.year
        y = self.calc(var, period=period, target=var_target)
        x = self.calc(wrt, period=period, target=wrt_target)
        try:
            y = y.squeeze()
        except:
            pass
        try:
            x = x.squeeze()
        except:
            pass
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        assert (
            len(y) > 1 and len(x) > 1
        ), "Simulation must vary on an axis to calculate derivatives."
        deriv = (y[1:] - y[:-1]) / (x[1:] - x[:-1])
        deriv = np.append(deriv, deriv[-1])
        return deriv

    def calc_mtr(
        self,
        target="household_net_income",
        wrt="employment_income",
        wrt_target=None,
        var_target=None,
    ):
        return 1 - self.calc_deriv(
            target, wrt=wrt, wrt_target=wrt_target, var_target=var_target
        )

    def reset_vary(self):
        del self.situation_data["axes"]
        self.varying = False
        self.num_points = None

    def vary(self, var, min=0, max=200000, step=100, index=0, period=None):
        period = period or self.year
        if "axes" not in self.situation_data:
            self.situation_data["axes"] = [[]]
        count = int((max - min) / step)
        self.situation_data["axes"][0] += [
            {
                "count": count,
                "name": var,
                "min": min,
                "max": max,
                "period": period,
                "index": index,
            }
        ]
        self.build()
        self.varying = True
        self.num_points = count