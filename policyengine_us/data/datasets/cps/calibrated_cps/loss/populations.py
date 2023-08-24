from typing import List, Tuple
import torch
import pandas as pd
from policyengine_core.data import Dataset
from survey_enhance.reweight import LossCategory
from policyengine_core.parameters import (
    ParameterNode,
    uprate_parameters,
    get_parameter,
)
from pathlib import Path
from survey_enhance.reweight import LossCategory
from policyengine_core.data import Dataset
import torch
from typing import List, Tuple
from policyengine_us.system import system
import numpy as np

class PopulationByAgeAndSex(LossCategory):
    def get_comparisons(
        self, dataset: Dataset
    ) -> List[Tuple[str, float, torch.Tensor]]:
        parameter = get_parameter(
            self.calibration_parameters, "us.populations.people.by_age_sex"
        )(self.instant)
        
        age = dataset.person.age
        is_male = dataset.person.is_male
        sex = np.where(is_male, "MALE", "FEMALE")

        person_household_id = dataset.person.household_id
        household_id = dataset.household.household_id

        comparisons = []

        for lower_age in range(0, 80, 5):
            for possible_sex in ("MALE", "FEMALE"):
                person_in_range = (age >= lower_age) * (age < lower_age + 5) * (sex == possible_sex)
                household_counts = person_in_range.groupby(person_household_id).sum()
                household_counts = household_counts[household_id].values
            
                comparisons.append((
                    f"{'Male' if possible_sex == 'MALE' else 'Female'} population between {lower_age} and {lower_age + 5}",
                    household_counts,
                    getattr(getattr(parameter, f"{lower_age}_{lower_age + 5}"), possible_sex),
                ))
    
        return comparisons