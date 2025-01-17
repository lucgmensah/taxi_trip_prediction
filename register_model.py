import mlflow

import common as common

MODEL_NAME = common.CONFIG['mlflow']['model_name']

def compare_runs_by_metrics(experiment_name):
    """
    Compare les runs d'une expérience MLflow en fonction des métriques R² et RMSE.
    
    :param experiment_name: Nom de l'expérience à analyser.
    :return: Dictionnaire contenant les informations du meilleur run.
    """
    # Initialiser le client MLflow
    client = mlflow.tracking.MlflowClient()
    
    # Rechercher l'expérience par nom
    experiments = mlflow.search_experiments(filter_string=f"name='{experiment_name}'")
    
    if not experiments:
        print(f"Aucune expérience trouvée avec le nom : {experiment_name}")
        return None
    
    # Obtenir l'ID de l'expérience
    experiment_id = experiments[0].experiment_id
    print(f"Expérience trouvée : {experiment_name} (ID: {experiment_id})")
    
    # Rechercher les runs terminés pour cette expérience
    runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string="status = 'FINISHED'",
        order_by=["metrics.r2 DESC", "metrics.rmse ASC"]
    )
    
    if runs.empty:
        print("Aucun run terminé trouvé dans cette expérience.")
        return None
    
    # Afficher et analyser les métriques des runs
    best_run = None
    print("Comparaison des métriques :")
    for _, run in runs.iterrows():
        run_id = run["run_id"]
        metrics = client.get_run(run_id).data.metrics
        r2 = metrics.get("r2", None)
        rmse = metrics.get("rmse", None)
        
        print(f"Run ID: {run_id} | R²: {r2} | RMSE: {rmse}")
        
        # Trouver le meilleur run
        if best_run is None:
            best_run = {"run_id": run_id, "r2": r2, "rmse": rmse}
        else:
            if r2 > best_run["r2"] or (r2 == best_run["r2"] and rmse < best_run["rmse"]):
                best_run = {"run_id": run_id, "r2": r2, "rmse": rmse}
    
    return best_run

if __name__ == "__main__":
    best_run = compare_runs_by_metrics("nyc_taxi_trip_duration")
    if best_run:
        print("\nLe meilleur run est :")
        print(best_run)
    
    # Register model 
    # Register the best model
    model_uri = f"runs:/{best_run['run_id']}/sklearn-model"
    mv = mlflow.register_model(model_uri, MODEL_NAME)
    print("Model saved to the model registry:")
    print(f"Name: {mv.name}")
    print(f"Version: {mv.version}")
    print(f"Source: {mv.source}")