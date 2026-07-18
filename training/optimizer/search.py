import optuna
import json
import os
import sys

# Ensure sibling packages are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from optimizer.fitness import HOLDOUT_DIR, evaluate_parameters

DB_PATH = "sqlite:///training/optimizer_state.db"
JSON_OUT = "training/dashboard/data.json"

def get_study(study_name="litedoc_tuning_v2"):
    """
    Creates or loads a persistent Optuna study using the Tree-structured
    Parzen Estimator (TPE) sampler for efficient Bayesian Optimization.

    v2: fresh study for the v3.0.0 order-aware fitness (scoring.py) and the OCR
    line-banding parser fix — scores are not comparable to the old objective, so
    old trials would only mislead TPE. The original "litedoc_tuning" study is
    preserved untouched in the same SQLite storage.
    """
    return optuna.create_study(
        study_name=study_name,
        storage=DB_PATH,
        load_if_exists=True,
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42)
    )

def objective(trial):
    """
    The objective function for Optuna.
    Maps Optuna's suggestions to LiteDoc's parameter structure.
    """
    # Full search space matching DEFAULT_CONFIG in src/core/layout/pdf-parser.js
    params = {
        "horizontalGapMultiplier": trial.suggest_float("horizontalGapMultiplier", 0.5, 2.0),
        "rowSplitMultiplier": trial.suggest_float("rowSplitMultiplier", 1.0, 6.0),
        "horizontalGapMin": trial.suggest_int("horizontalGapMin", 4, 30),
        "bottomMarginThreshold": trial.suggest_float("bottomMarginThreshold", 0.80, 0.98),
        "topMarginThreshold": trial.suggest_float("topMarginThreshold", 0.02, 0.15),
        "distanceFromCenterPenalty": trial.suggest_float("distanceFromCenterPenalty", 1.0, 6.0),
        "tableDensityThreshold": trial.suggest_float("tableDensityThreshold", 0.2, 0.9),
        "pageGarbageRatioThreshold": trial.suggest_float("pageGarbageRatioThreshold", 0.3, 0.95),
        "paragraphGapThreshold": trial.suggest_float("paragraphGapThreshold", 1.0, 3.0),
        "continuationGapThreshold": trial.suggest_float("continuationGapThreshold", 0.8, 3.0),
        "tableGapYThreshold": trial.suggest_float("tableGapYThreshold", 1.5, 6.0),
        "gapMultiplier": trial.suggest_float("gapMultiplier", 0.4, 2.0),
        "ocrTolMultiplier": trial.suggest_float("ocrTolMultiplier", 1.0, 6.0),
    }
    
    score, breakdown = evaluate_parameters(params)
    
    # Update dashboard JSON
    update_dashboard(trial.number, score, params, breakdown)
    
    return score

def update_dashboard(trial_num, score, params, breakdown):
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    
    data = []
    if os.path.exists(JSON_OUT):
        with open(JSON_OUT, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
                
    data.append({
        "generation": trial_num,
        "score": score,
        "params": params,
        "breakdown": breakdown
    })
    
    with open(JSON_OUT, 'w') as f:
        json.dump(data, f, indent=2)

def run_optimization(n_trials=500):
    study = get_study()
    print(f"Resuming study. Currently at {len(study.trials)} completed trials.")

    try:
        study.optimize(objective, n_trials=n_trials, catch=(Exception,))
    except KeyboardInterrupt:
        print("\nOptimization interrupted. State securely saved to SQLite.")

    print("\nBest Parameters (train set — training/source_materials):")
    print(study.best_params)
    print(f"Train Score: {study.best_value}")

    holdout_score = validate_on_holdout(study.best_params, study.best_value)
    save_best_params(study.best_params, study.best_value, holdout_score)


def run_forever():
    """
    Runs the Optuna search indefinitely — meant for a systemd service with
    Restart=always, not interactive use. Trials persist to optimizer_state.db as
    they complete, so a crash/restart resumes rather than losing progress.
    Does NOT do holdout validation or write current_params.json itself — that's
    notify_weekly.py's job, run on a separate schedule against whatever the study's
    current best is at check time.
    """
    study = get_study()
    print(f"Starting continuous optimization. Currently at {len(study.trials)} completed trials.")
    study.optimize(objective, n_trials=None, catch=(Exception,))


def validate_on_holdout(params, train_score):
    """
    Score the winning params against a held-out set the Optuna search never saw.
    This is the only number that estimates generalization — the train score just
    confirms the search found *something* that fits training/source_materials,
    which it was explicitly optimizing to do.
    """
    if not os.path.isdir(HOLDOUT_DIR) or not any(os.scandir(HOLDOUT_DIR)):
        print(
            f"\n[WARN] No held-out set found at {HOLDOUT_DIR}/ — the score above is train-set "
            f"performance only, not a generalization estimate. Run "
            f"'python training/orchestrator.py --synthesize-holdout <N>' to add one, then re-run "
            f"--optimize (or just point benchmark_ab.py at {HOLDOUT_DIR})."
        )
        return None

    print(f"\nValidating best params against held-out set ({HOLDOUT_DIR}/, never seen during search)...")
    holdout_score, _ = evaluate_parameters(params, data_dir=HOLDOUT_DIR)
    print(f"Holdout Score: {holdout_score}")

    if train_score > 0:
        gap = train_score - holdout_score
        if gap > train_score * 0.15:
            print(
                f"[WARN] Holdout score is {gap * 100:.1f} points lower than train score — "
                f"the search may be overfitting to training/source_materials. Consider a larger "
                f"or more diverse synthetic dataset before trusting these params."
            )
    return holdout_score


def save_best_params(params, train_score=None, holdout_score=None):
    """Write the best-known parameters to current_params.json for LiteDoc to consume."""
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "current_params.json")
    payload = dict(params)
    if train_score is not None:
        payload["_trainScore"] = train_score
    if holdout_score is not None:
        payload["_holdoutScore"] = holdout_score

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved best params to {out_path}")
