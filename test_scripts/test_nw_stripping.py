import numpy as np
import pandas as pd
import theoretical_nn_training.data_processing as data
import torch
from theoretical_nn_training.configuration import NNConfig
from theoretical_nn_training.generators import SurfaceGenerator


def main() -> None:
    config = NNConfig("theoretical_nn_training/configurations/mixed_config_512.yaml")
    config.batch_size = 1
    config.device = torch.device("cpu")

    gen = SurfaceGenerator(config)

    num_surfaces = 3
    feats = np.zeros((num_surfaces, 3))

    for i, (surf, feat) in enumerate(gen(3)):
        feats[i] = [
            data.unnormalize_feature(f, r).numpy()
            for f, r in zip(
                feat.ravel(),
                [config.bg_range, config.bth_range, config.pe_range],
            )
        ]
        surf = data.unnormalize_eta_sp(
            surf.reshape((-1, 1)), config.eta_sp_range
        ).numpy()
        flattened_phi_Nw_mesh = gen.flattened_phi_Nw_mesh.numpy()
        df = pd.DataFrame(
            np.concatenate((flattened_phi_Nw_mesh, surf), axis=1),
            columns=["phi", "Nw", "eta_sp"],
        )
        print(df)
        df.to_csv(f"../mike_outputs/surface_{i}.csv", index=False)
        np.savetxt(
            "../mike_outputs/features.csv",
            feats,
            delimiter=",",
        )


if __name__ == "__main__":
    main()
