from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Basic experiment params
    seed: int
    pop_size: int
    num_gen: int
    cross_rate: float
    mut_rate: float
    experiment_count: int
    # Shared/fixed params (example)
    individual_size: int
    sample_count: int
    classifier_path: str
    tournament_size: int
    name_test_file: str
    class_name_test_file: str
    # Need info for ML model and data files
    classifier_name: str
    ml_model_params: list # Or dict
    output_base_dir: str