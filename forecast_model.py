"""
SmartCash AI - Moteur de Prévision Intelligente par Machine Learning
Module forecast_model.py
Construit les variables temporelles, entraîne et évalue un modèle Scikit-learn
(Random Forest / Ridge) pour projeter le flux net et le solde de trésorerie futur.
Intègre un basculement rigoureux vers une méthode de référence si les données sont insuffisantes.
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

def prepare_time_series_features(daily_df: pd.DataFrame, max_lags: int = 7) -> pd.DataFrame:
    """
    Construit les variables explicatives temporelles (Feature Engineering) :
    - Composantes calendaires (jour de la semaine, jour du mois, mois, weekend)
    - Encodage cyclique (sinus / cosinus)
    - Décalages temporels (Lags à J-1, J-2, J-7)
    - Statistiques glissantes (Moyenne et écart-type sur 7 jours)
    """
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date").reset_index(drop=True)

    # 1. Variables calendaires
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 2. Encodage cyclique (pour capturer la périodicité calendaire)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
    df["dom_sin"] = np.sin(2 * np.pi * df["day_of_month"] / 31.0)
    df["dom_cos"] = np.cos(2 * np.pi * df["day_of_month"] / 31.0)

    # 3. Lags (valeurs passées du flux net)
    df["lag_1"] = df["flux_net"].shift(1)
    df["lag_2"] = df["flux_net"].shift(2)
    df["lag_7"] = df["flux_net"].shift(7)

    # 4. Statistiques glissantes
    df["rolling_mean_7"] = df["flux_net"].shift(1).rolling(window=7, min_periods=1).mean()
    df["rolling_std_7"] = df["flux_net"].shift(1).rolling(window=7, min_periods=1).std().fillna(0.0)

    return df

def train_and_forecast_cashflow(
    df_raw: pd.DataFrame,
    initial_balance: float = 120000.0,
    horizon_days: int = 15,
    model_type: str = "Random Forest (IA)",
    test_size_days: int = 14
):
    """
    Entraîne le modèle prédictif sur l'historique réalisé et génère
    les prévisions journalières sur l'horizon choisi (7, 15, 30 jours).
    
    Retourne un dictionnaire contenant :
    - forecast_df : DataFrame des prévisions (date, flux_prevu, solde_prevu, bornes)
    - evaluation : métriques réelles (MAE, RMSE, R2, df_test_eval)
    - model_info : type de modèle retenu, importance des variables, explications
    - is_fallback : booléen indiquant si une méthode de référence a été utilisée
    """
    if df_raw.empty:
        return None

    # Filtrer les opérations réalisées pour l'apprentissage historique
    realized_df = df_raw[df_raw["statut"] == "Réalisé"].copy()
    planned_df = df_raw[df_raw["statut"] == "Prévu"].copy()

    from financial_calculations import compute_daily_cashflow
    daily_history = compute_daily_cashflow(realized_df, initial_balance=initial_balance)
    
    if daily_history.empty:
        return None

    num_historical_days = len(daily_history)
    last_historical_date = daily_history["date"].max()
    current_balance = daily_history["solde_cumule"].iloc[-1]

    # Vérification du volume de données historiques (Condition de rigueur académique)
    MIN_DAYS_FOR_ML = 21

    if num_historical_days < MIN_DAYS_FOR_ML:
        # Repli propre sur méthode de référence (Moyenne mobile et tendance simple)
        return _forecast_baseline(
            daily_history=daily_history,
            planned_df=planned_df,
            current_balance=current_balance,
            last_date=last_historical_date,
            horizon_days=horizon_days,
            reason=f"Historique disponible ({num_historical_days} jours) inférieur au seuil minimal recommandé ({MIN_DAYS_FOR_ML} jours) pour un entraînement ML rigoureux."
        )

    # Préparation des variables
    featured_df = prepare_time_series_features(daily_history)
    # Suppression des lignes avec NaN dues aux lags
    trainable_df = featured_df.dropna(subset=["lag_1", "lag_2", "lag_7"]).copy()

    feature_cols = [
        "day_of_week", "day_of_month", "month", "is_weekend",
        "dow_sin", "dow_cos", "dom_sin", "dom_cos",
        "lag_1", "lag_2", "lag_7", "rolling_mean_7", "rolling_std_7"
    ]

    # Découpage Temporel Train / Test (sans fuite temporelle)
    actual_test_days = min(test_size_days, max(5, int(len(trainable_df) * 0.2)))
    train_data = trainable_df.iloc[:-actual_test_days]
    test_data = trainable_df.iloc[-actual_test_days:]

    X_train = train_data[feature_cols]
    y_train = train_data["flux_net"]
    X_test = test_data[feature_cols]
    y_test = test_data["flux_net"]

    # Choix et entraînement du modèle
    if "Ridge" in model_type:
        model = Ridge(alpha=10.0, random_state=42)
        model_name = "Régression Linéaire Régularisée (Ridge)"
    else:
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            min_samples_split=4,
            random_state=42
        )
        model_name = "Forêt Aléatoire (Random Forest Regressor)"

    model.fit(X_train, y_train)

    # Évaluation sur l'échantillon test
    y_pred_test = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred_test)
    rmse = root_mean_squared_error(y_test, y_pred_test)
    r2 = r2_score(y_test, y_pred_test)

    eval_df = test_data[["date", "flux_net"]].copy()
    eval_df["flux_reel"] = y_test.values
    eval_df["flux_predit"] = y_pred_test
    eval_df["date_str"] = eval_df["date"].dt.strftime("%Y-%m-%d")

    # Importance des variables (Feature Importance)
    feature_importance = {}
    if hasattr(model, "feature_importances_"):
        for col, imp in zip(feature_cols, model.feature_importances_):
            feature_importance[col] = round(float(imp) * 100, 2)
    elif hasattr(model, "coef_"):
        for col, coef in zip(feature_cols, model.coef_):
            feature_importance[col] = round(float(abs(coef)), 2)

    # Ré-entraînement sur tout l'historique pour maximiser la qualité future
    X_full = trainable_df[feature_cols]
    y_full = trainable_df["flux_net"]
    model.fit(X_full, y_full)

    # Projection pas à pas sur l'horizon futur (Auto-régression itérative)
    future_records = []
    running_balance = current_balance
    last_series = daily_history.copy()

    # Pré-agréger les opérations prévues saisies par l'utilisateur
    planned_daily = {}
    if not planned_df.empty:
        p_df = planned_df.copy()
        p_df["date"] = pd.to_datetime(p_df["date"])
        p_pivot = p_df.groupby(["date", "type"])["montant"].sum().unstack(fill_value=0.0).reset_index()
        for _, p_row in p_pivot.iterrows():
            d_key = p_row["date"].strftime("%Y-%m-%d")
            enc = p_row.get("Encaissement", 0.0)
            dec = p_row.get("Décaissement", 0.0)
            planned_daily[d_key] = enc - dec

    curr_date = last_historical_date + timedelta(days=1)
    
    # Calcul de la volatilité historique pour les intervalles de confiance (IC à 80%)
    std_residuals = float(np.std(y_test.values - y_pred_test)) if len(y_test) > 0 else 500.0
    if std_residuals < 100.0:
        std_residuals = 500.0

    for step in range(1, horizon_days + 1):
        d_str = curr_date.strftime("%Y-%m-%d")
        dow = curr_date.weekday()
        dom = curr_date.day
        mo = curr_date.month
        is_we = 1 if dow in [5, 6] else 0

        dow_sin = np.sin(2 * np.pi * dow / 7.0)
        dow_cos = np.cos(2 * np.pi * dow / 7.0)
        dom_sin = np.sin(2 * np.pi * dom / 31.0)
        dom_cos = np.cos(2 * np.pi * dom / 31.0)

        # Lags depuis la série enrichie
        lag_1 = last_series["flux_net"].iloc[-1]
        lag_2 = last_series["flux_net"].iloc[-2] if len(last_series) >= 2 else lag_1
        lag_7 = last_series["flux_net"].iloc[-7] if len(last_series) >= 7 else lag_1
        roll_7 = last_series["flux_net"].iloc[-7:].mean() if len(last_series) >= 7 else lag_1
        roll_std_7 = last_series["flux_net"].iloc[-7:].std() if len(last_series) >= 7 else 0.0
        if np.isnan(roll_std_7):
            roll_std_7 = 0.0

        x_future = pd.DataFrame([{
            "day_of_week": dow,
            "day_of_month": dom,
            "month": mo,
            "is_weekend": is_we,
            "dow_sin": dow_sin,
            "dow_cos": dow_cos,
            "dom_sin": dom_sin,
            "dom_cos": dom_cos,
            "lag_1": lag_1,
            "lag_2": lag_2,
            "lag_7": lag_7,
            "rolling_mean_7": roll_7,
            "rolling_std_7": roll_std_7
        }])[feature_cols]

        pred_flux_ml = float(model.predict(x_future)[0])

        # Si le jour est un weekend, ajuster le flux commercial vers zéro (sauf opération prévue explicite)
        if is_we:
            pred_flux_ml = pred_flux_ml * 0.15

        # Intégration hybride : Opération prévue certaine + composante statistique
        planned_flow = planned_daily.get(d_str, None)
        if planned_flow is not None:
            # L'opération déjà planifiée prédomine avec ajout du bruit tendanciel
            flux_net_jour = planned_flow + (pred_flux_ml * 0.3)
        else:
            flux_net_jour = pred_flux_ml

        running_balance += flux_net_jour
        uncertainty = std_residuals * np.sqrt(step) * 1.28  # Intervalle à ~80%

        future_records.append({
            "date": curr_date,
            "date_str": d_str,
            "flux_prevu": round(flux_net_jour, 2),
            "solde_prevu": round(running_balance, 2),
            "borne_inf": round(running_balance - uncertainty, 2),
            "borne_sup": round(running_balance + uncertainty, 2),
            "type_modele": model_name
        })

        # Mettre à jour la série pour les lags suivants
        new_row = pd.DataFrame([{
            "date": curr_date,
            "encaissements": max(0.0, flux_net_jour),
            "decaissements": abs(min(0.0, flux_net_jour)),
            "flux_net": flux_net_jour,
            "solde_cumule": running_balance,
            "date_str": d_str
        }])
        last_series = pd.concat([last_series, new_row], ignore_index=True)
        curr_date += timedelta(days=1)

    forecast_df = pd.DataFrame(future_records)

    return {
        "forecast_df": forecast_df,
        "evaluation": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 3),
            "eval_df": eval_df,
            "train_size": len(train_data),
            "test_size": len(test_data)
        },
        "model_info": {
            "name": model_name,
            "features": feature_cols,
            "importance": feature_importance,
            "explication": "Le modèle exploite les récurrences calendaires, la cyclicité hebdomadaire et les opérations planifiées pour estimer l'évolution prévisionnelle."
        },
        "is_fallback": False
    }

def _forecast_baseline(daily_history, planned_df, current_balance, last_date, horizon_days, reason):
    """Méthode de référence simple (Moyenne mobile / tendance) en cas de données restreintes."""
    mean_flux = daily_history["flux_net"].mean() if not daily_history.empty else 0.0
    future_records = []
    running_balance = current_balance
    curr_date = last_date + timedelta(days=1)

    # Récupération des opérations prévues
    planned_daily = {}
    if not planned_df.empty:
        p_df = planned_df.copy()
        p_df["date"] = pd.to_datetime(p_df["date"])
        p_pivot = p_df.groupby(["date", "type"])["montant"].sum().unstack(fill_value=0.0).reset_index()
        for _, p_row in p_pivot.iterrows():
            d_key = p_row["date"].strftime("%Y-%m-%d")
            enc = p_row.get("Encaissement", 0.0)
            dec = p_row.get("Décaissement", 0.0)
            planned_daily[d_key] = enc - dec

    std_flux = daily_history["flux_net"].std() if len(daily_history) > 1 else 300.0

    for step in range(1, horizon_days + 1):
        d_str = curr_date.strftime("%Y-%m-%d")
        planned_flow = planned_daily.get(d_str, None)
        if planned_flow is not None:
            flux_jour = planned_flow
        else:
            flux_jour = mean_flux if curr_date.weekday() not in [5, 6] else 0.0

        running_balance += flux_jour
        uncertainty = std_flux * np.sqrt(step)

        future_records.append({
            "date": curr_date,
            "date_str": d_str,
            "flux_prevu": round(flux_jour, 2),
            "solde_prevu": round(running_balance, 2),
            "borne_inf": round(running_balance - uncertainty, 2),
            "borne_sup": round(running_balance + uncertainty, 2),
            "type_modele": "Méthode de référence (Moyenne mobile empirique)"
        })
        curr_date += timedelta(days=1)

    forecast_df = pd.DataFrame(future_records)
    return {
        "forecast_df": forecast_df,
        "evaluation": {
            "mae": None,
            "rmse": None,
            "r2": None,
            "eval_df": pd.DataFrame(),
            "reason": reason
        },
        "model_info": {
            "name": "Méthode de référence (Moyenne mobile empirique)",
            "features": ["Historique moyen", "Opérations prévues"],
            "importance": {},
            "explication": reason
        },
        "is_fallback": True
    }

