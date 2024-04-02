import torch
import pandas as pd
import numpy as np
from tqdm import tqdm
import numpy as np
import pandas as pd
from pathlib import Path
from policyengine_us.data.datasets.cps.enhanced_cps.loss import (
    generate_model_variables,
)


def aggregate(
    adjusted_weights: torch.Tensor, values: pd.DataFrame
) -> torch.Tensor:
    broadcasted_weights = adjusted_weights.reshape(-1, 1)
    weighted_values = torch.matmul(
        broadcasted_weights.T, torch.tensor(values.values, dtype=torch.float32)
    )
    return weighted_values


def calibrate(
    dataset: str,
    time_period: str = "2022",
    training_log_path: str = "training_log.csv.gz",
    learning_rate: float = 2e1,
    epochs: int = 10_000,
) -> np.ndarray:
    (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
        equivalisation_factors_array,
    ) = generate_model_variables(dataset, time_period)
    household_weights = torch.tensor(household_weights, dtype=torch.float32)
    weight_adjustment = torch.tensor(
        weight_adjustment, dtype=torch.float32, requires_grad=True
    )
    targets_array = torch.tensor(targets_array, dtype=torch.float32)
    equivalisation_factors_array = torch.tensor(
        equivalisation_factors_array, dtype=torch.float32
    )
    training_log_path = Path(training_log_path)
    if training_log_path.exists():
        training_log_df = pd.read_csv(training_log_path, compression="gzip")
    else:
        training_log_df = pd.DataFrame()

    progress_bar = tqdm(range(epochs), desc="Calibrating weights")
    optimizer = torch.optim.Adam([weight_adjustment], lr=learning_rate)
    for i in progress_bar:
        adjusted_weights = torch.relu(household_weights + weight_adjustment)
        result = (
            aggregate(adjusted_weights, values_df)
            / equivalisation_factors_array
        )
        target = targets_array / equivalisation_factors_array
        loss = torch.mean(
            ((result / target - 1) ** 2) * np.log2(np.abs(target))
        )
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if i % 10 == 0:
            current_loss = loss.item()
            progress_bar.set_description_str(
                f"Calibrating weights | Loss = {current_loss:,.3f}"
            )
        if i % 2_000 == 0:
            current_aggregates = (
                (result * equivalisation_factors_array).detach().numpy()[0]
            )
            training_log_df = pd.concat(
                [
                    training_log_df,
                    pd.DataFrame(
                        {
                            "name": list(targets.keys()) + ["total"],
                            "epoch": [i] * len(targets) + [i],
                            "value": list(current_aggregates) + [current_loss],
                            "target": list(targets.values()) + [0],
                            "time_period": time_period,
                        }
                    ),
                ]
            )
            training_log_df.to_csv(training_log_path, compression="gzip")

    return adjusted_weights.detach().numpy()
