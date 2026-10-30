"""
SmartCash AI - Générateur de Rapports PDF & Exports (Contexte Marocain 🇲🇦)
Module report_generator.py
Produit des synthèses exécutives professionnelles au format PDF (via fpdf2)
avec montants en Dirhams Marocains (DH / MAD) et références aux pratiques comptables du Maroc.
"""

import io
from datetime import datetime, date
from fpdf import FPDF
import pandas as pd
from data_manager import format_dh, get_now_morocco

def _clean_str(text: str) -> str:
    """Nettoie les caractères pour compatibilité stricte avec les polices standard FPDF."""
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "—": "-", "–": "-", "’": "'", "‘": "'",
        "“": '"', "”": '"', "…": "...", "€": "DH",
        "«": '"', "»": '"', "\xa0": " ", "🇲🇦": ""
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s.encode("latin-1", "replace").decode("latin-1")

class SmartCashPDF(FPDF):
    def header(self):
        # Bandeau supérieur bleu marine foncé
        self.set_fill_color(11, 22, 48) # #0B1630
        self.rect(0, 0, 210, 24, 'F')
        
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(241, 245, 249) # #F1F5F9
        self.set_xy(10, 5)
        self.cell(0, 8, _clean_str("SmartCash AI Maroc | Rapport Exécutif de Trésorerie"), ln=True)
        
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(183, 197, 218) # #B7C5DA
        self.set_xy(10, 13)
        self.cell(0, 6, _clean_str("Votre trésorerie, anticipée intelligemment | Contexte Entreprises Maroc (MAD)"), ln=True)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 150, 170)
        self.cell(0, 10, _clean_str(f"SmartCash AI Maroc - Page {self.page_no()}/{{nb}} - Document d'aide à la décision financière"), align="C")

def generate_pdf_report(kpis: dict, adv: dict, alerts: list, forecast_data: dict = None) -> bytes:
    """Génère un rapport financier complet et soigné au format PDF en DH."""
    pdf = SmartCashPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    # Titre du rapport & Date
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(16, 31, 61) # #101F3D
    now_maroc = get_now_morocco()
    date_str = now_maroc.strftime("%d/%m/%Y à %H:%M")
    pdf.set_x(10)
    pdf.cell(0, 8, _clean_str("SYNTHÈSE FINANCIÈRE & PRÉVISION DE TRÉSORERIE (DH)"), ln=True)
    
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(10)
    pdf.cell(0, 6, _clean_str(f"Édité le {date_str} (Heure de Casablanca) | Entreprise : Atlas Distribution SARL"), ln=True)
    pdf.ln(3)

    # 1. Indicateurs Clés de Performance (KPIs)
    pdf.set_x(10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(16, 31, 61)
    pdf.cell(190, 7.5, _clean_str(" 1. INDICATEURS FINANCIERS DE TRÉSORERIE (EN DIRHAMS MAROCAINS)"), fill=True, ln=True)
    pdf.ln(2.5)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)

    col_w = 47.5
    h = 6.5

    # Ligne 1
    pdf.set_x(10)
    pdf.cell(col_w, h, _clean_str("Solde Actuel :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('solde_actuel', 0))), border=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Solde Prévisionnel :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('solde_previsionnel', 0))), border=1, ln=True)

    # Ligne 2
    pdf.set_x(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Total Encaissements :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('total_encaissements', 0))), border=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Total Décaissements :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('total_decaissements', 0))), border=1, ln=True)

    # Ligne 3 - Créances & Dettes
    pdf.set_x(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Créances Clients :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('creances_clients', 0))), border=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Dettes Fournisseurs :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('dettes_fournisseurs', 0))), border=1, ln=True)

    # Ligne 4 - Ratios & Risque
    pdf.set_x(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Ratio de Couverture :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(f"{adv.get('coverage_ratio', 1.0):.2f}"), border=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Niveau de Risque :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(f"{kpis.get('niveau_risque', 'Faible')}"), border=1, ln=True)

    # Ligne 5 - Autonomie & TVA
    pdf.set_x(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("Autonomie (Runway) :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(f"{adv.get('runway_days', 0)} jours"), border=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, h, _clean_str("TVA Nette Due DGI :"), border=1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, h, _clean_str(format_dh(kpis.get('tva_due', 0))), border=1, ln=True)

    pdf.ln(4)

    # 2. Répartition des Principales Charges (PCGE)
    pdf.set_x(10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(16, 31, 61)
    pdf.cell(190, 7.5, _clean_str(" 2. PRINCIPAUX POSTES DE CHARGES (PCGE MAROCAIN)"), fill=True, ln=True)
    pdf.ln(2.5)

    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(105, 6, _clean_str("Catégorie de Charge (PCGE)"), border=1, fill=True)
    pdf.cell(50, 6, _clean_str("Montant Total (DH)"), border=1, fill=True, align="R")
    pdf.cell(35, 6, _clean_str("Part (%)"), border=1, fill=True, align="R", ln=True)

    pdf.set_font("Helvetica", "", 8.5)
    cat_df = adv.get("cat_expenses", pd.DataFrame())
    if not cat_df.empty:
        for _, row in cat_df.head(5).iterrows():
            pdf.set_x(10)
            pdf.cell(105, 5.8, _clean_str(str(row["categorie"])), border=1)
            pdf.cell(50, 5.8, _clean_str(format_dh(row['montant'], include_symbol=False)), border=1, align="R")
            pdf.cell(35, 5.8, _clean_str(f"{row['pct']:.1f}%"), border=1, align="R", ln=True)
    else:
        pdf.set_x(10)
        pdf.cell(190, 6, _clean_str("Aucun décaissement enregistré sur la période."), border=1, ln=True)

    pdf.ln(4)

    # 3. Prévisions d'Intelligence Artificielle
    pdf.set_x(10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(16, 31, 61)
    pdf.cell(190, 7.5, _clean_str(" 3. DIAGNOSTIC DU MODÈLE DE MACHINE LEARNING"), fill=True, ln=True)
    pdf.ln(2.5)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    if forecast_data:
        m_name = forecast_data.get("model_info", {}).get("name", "Machine Learning")
        eval_metrics = forecast_data.get("evaluation", {})
        mae = eval_metrics.get("mae")
        r2 = eval_metrics.get("r2")
        is_fallback = forecast_data.get("is_fallback", False)
        
        pdf.set_x(10)
        pdf.multi_cell(190, 4.8, _clean_str(f"Modèle d'apprentissage : {m_name}\n"
                                          f"Méthodologie : Apprentissage supervisé par régression sur les flux nets en DH. Intègre les récurrences hebdomadaires, cycles calendaires, échéances d'impôts DGI/CNSS et factures déjà ordonnancées."))
        pdf.ln(1.5)
        if not is_fallback and mae is not None:
            pdf.set_x(10)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.cell(190, 5, _clean_str(f"Performance sur échantillon test : Erreur Moyenne Absolue (MAE) = {format_dh(mae)} | R2 = {r2}"), ln=True)
            pdf.set_font("Helvetica", "", 8.5)
        elif is_fallback:
            pdf.set_x(10)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.cell(190, 5, _clean_str("Méthode de référence : Historique restreint, projection prudente basée sur moyenne mobile."), ln=True)
            pdf.set_font("Helvetica", "", 8.5)
    else:
        pdf.set_x(10)
        pdf.cell(190, 5, _clean_str("Prévisions non calculées."), ln=True)

    pdf.ln(4)

    # 4. Alertes & Recommandations Managériales
    pdf.set_x(10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(16, 31, 61)
    pdf.cell(190, 7.5, _clean_str(" 4. ALERTES ET RECOMMANDATIONS MANAGÉRIALES (MAROC)"), fill=True, ln=True)
    pdf.ln(2.5)

    if alerts:
        for idx, alt in enumerate(alerts[:3], start=1):
            pdf.set_x(10)
            pdf.set_font("Helvetica", "B", 9)
            grav = alt.get("gravite", "Info").upper()
            if grav in ["CRITIQUE", "ÉLEVÉ"]:
                pdf.set_text_color(220, 38, 38)
            else:
                pdf.set_text_color(16, 31, 61)
            pdf.cell(190, 5.5, _clean_str(f"[{grav}] {alt.get('titre')} (Échéance : {alt.get('date')})"), ln=True)
            
            pdf.set_x(10)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(190, 4.5, _clean_str(f"Constat : {alt.get('raison')}"))
            
            pdf.set_x(10)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.multi_cell(190, 4.5, _clean_str(f"Recommandation : {alt.get('recommandation')}"))
            pdf.ln(1.5)
    else:
        pdf.set_x(10)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(190, 5.5, _clean_str("Aucun risque financier critique détecté."), ln=True)

    return bytes(pdf.output())
