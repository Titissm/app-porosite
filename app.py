import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Visualiser la porosité", layout="wide")
st.title("🪨 Visualiser la porosité")
st.caption("Application pédagogique – Sciences de la Terre (L3)")

M2_PAR_MD = 9.869e-16  # 1 millidarcy en m²
BBL_PAR_M3 = 6.2898  # 1 m³ en barils

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["1. Calcul", "2. Grains", "3. Compaction", "4. Perméabilité", "5. Fractures", "6. Réservoir"]
)

# ---------------------------------------------------------------
# Onglet 1 : calcul de la porosité
# ---------------------------------------------------------------
with tab1:
    st.latex(r"\phi = \frac{V_{vides}}{V_{total}}")
    methode = st.radio("Données connues", ["Masses volumiques", "Volumes"], horizontal=True)

    if methode == "Masses volumiques":
        st.latex(r"\phi = 1 - \frac{\rho_{apparente}}{\rho_{grains}}")
        rho_grains = st.number_input("Masse volumique des grains (g/cm³)", 1.0, 5.0, 2.65, 0.01)
        rho_app = st.number_input("Masse volumique apparente sèche (g/cm³)", 0.5, 4.0, 2.00, 0.01)
        phi = 1 - rho_app / rho_grains
    else:
        v_total = st.number_input("Volume total de l'échantillon (cm³)", 1.0, 1000.0, 100.0, 1.0)
        v_solide = st.number_input("Volume des grains (cm³)", 1.0, 1000.0, 70.0, 1.0)
        phi = (v_total - v_solide) / v_total

    if not 0 <= phi <= 1:
        st.error("Valeurs incohérentes : la porosité doit être comprise entre 0 et 100 %.")
    else:
        st.metric("Porosité φ", f"{phi * 100:.1f} %")
        fig, ax = plt.subplots(figsize=(6, 1.2))
        ax.barh([0], [1 - phi], color="tan", label="Grains (solide)")
        ax.barh([0], [phi], left=[1 - phi], color="steelblue", label="Vides (pores)")
        ax.set_xlim(0, 1)
        ax.axis("off")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, frameon=False)
        st.pyplot(fig)

    st.markdown(
        "**Repères** : empilement cubique de sphères ≈ 47,6 % ; "
        "empilement rhomboédrique (le plus compact) ≈ 26,0 %."
    )

# ---------------------------------------------------------------
# Onglet 2 : empilement de grains en 2D
# ---------------------------------------------------------------
def empiler_grains(n, r_moy, sigma, graine):
    """Place des grains circulaires sans chevauchement dans un carré de côté 1."""
    rng = np.random.default_rng(graine)
    grains = []
    for _ in range(n * 50):  # nombre d'essais limité
        if len(grains) == n:
            break
        r = float(np.clip(rng.normal(r_moy, sigma), 0.01, 0.2))
        x, y = rng.uniform(r, 1 - r, 2)
        if all((x - gx) ** 2 + (y - gy) ** 2 >= (r + gr) ** 2 for gx, gy, gr in grains):
            grains.append((x, y, r))
    return grains


with tab2:
    st.write(
        "Les grains sont tirés au hasard puis placés sans se chevaucher. "
        "Les vides entre les grains forment la porosité."
    )
    col_a, col_b = st.columns([1, 2])
    with col_a:
        n = st.slider("Nombre de grains souhaité", 10, 400, 80)
        r_moy = st.slider("Rayon moyen des grains", 0.01, 0.10, 0.04, 0.005)
        sigma = st.slider("Dispersion des tailles (tri)", 0.0, 0.05, 0.005, 0.001)
        graine = st.number_input("Graine aléatoire", 0, 9999, 1)
        st.caption("Dispersion faible = sédiment bien classé ; forte = mal classé.")

    grains = empiler_grains(n, r_moy, sigma, int(graine))
    aire_grains = sum(np.pi * r**2 for _, _, r in grains)
    phi_2d = 1 - aire_grains  # aire du carré = 1

    with col_b:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor("steelblue")  # le fond = les pores
        for x, y, r in grains:
            ax.add_patch(plt.Circle((x, y), r, color="tan", ec="saddlebrown"))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        st.pyplot(fig)

    col_a.metric("Grains placés", len(grains))
    col_a.metric("Porosité 2D", f"{phi_2d * 100:.1f} %")
    if len(grains) < n:
        col_a.warning("Le milieu est saturé : impossible de placer tous les grains.")

# ---------------------------------------------------------------
# Onglet 3 : porosité en fonction de la profondeur (loi d'Athy)
# ---------------------------------------------------------------
# (phi0, c) : porosité en surface et coefficient de compaction (km⁻¹)
# Valeurs indicatives d'après Sclater & Christie (1980)
LITHOLOGIES = {
    "Sable": (0.49, 0.27),
    "Sable argileux": (0.56, 0.39),
    "Argile (shale)": (0.63, 0.51),
    "Craie": (0.70, 0.71),
}

with tab3:
    st.latex(r"\phi(z) = \phi_0 \, e^{-c\,z}")
    st.write(
        "La porosité diminue avec l'enfouissement car les grains se réarrangent "
        "et l'eau est expulsée (compaction mécanique)."
    )
    choix = st.multiselect(
        "Lithologies", list(LITHOLOGIES), default=["Sable", "Argile (shale)"]
    )
    z_max = st.slider("Profondeur maximale (km)", 1.0, 8.0, 5.0, 0.5)
    z_lue = st.slider("Profondeur à lire (km)", 0.0, z_max, 2.0, 0.1)

    z = np.linspace(0, z_max, 200)
    fig, ax = plt.subplots(figsize=(6, 5))
    for nom in choix:
        phi0, c = LITHOLOGIES[nom]
        ax.plot(np.exp(-c * z) * phi0 * 100, z, label=nom)
    ax.axhline(z_lue, color="grey", linestyle="--")
    ax.set_xlabel("Porosité (%)")
    ax.set_ylabel("Profondeur (km)")
    ax.set_xlim(0, 80)
    ax.invert_yaxis()  # la profondeur augmente vers le bas
    ax.grid(alpha=0.3)
    if choix:
        ax.legend()
    st.pyplot(fig)

    if choix:
        colonnes = st.columns(len(choix))
        for col, nom in zip(colonnes, choix):
            phi0, c = LITHOLOGIES[nom]
            col.metric(f"{nom} à {z_lue:.1f} km", f"{phi0 * np.exp(-c * z_lue) * 100:.1f} %")

# ---------------------------------------------------------------
# Onglet 4 : perméabilité (Kozeny-Carman)
# ---------------------------------------------------------------
def kozeny_carman(phi, d):
    """Perméabilité (m²) d'un empilement de grains sphériques de diamètre d (m)."""
    return phi**3 / (1 - phi) ** 2 * d**2 / 180


with tab4:
    st.latex(r"k = \frac{\phi^3}{(1-\phi)^2} \cdot \frac{d^2}{180}")
    st.write(
        "La perméabilité k mesure l'aptitude d'une roche à laisser circuler un fluide "
        "(loi de Darcy). Ici on l'estime à partir de la porosité φ et du diamètre d des grains."
    )
    col_a, col_b = st.columns([1, 2])
    with col_a:
        phi_kc = st.slider("Porosité φ (%)", 5, 50, 30) / 100
        d_um = st.slider("Diamètre des grains d (µm)", 10, 2000, 200, 10)
        k = kozeny_carman(phi_kc, d_um * 1e-6)
        st.metric("Perméabilité k", f"{k / M2_PAR_MD:,.0f} mD")
        st.caption(f"= {k:.2e} m² ≈ {k / M2_PAR_MD / 1000:.2f} darcy")

    with col_b:
        phis = np.linspace(0.05, 0.5, 100)
        fig, ax = plt.subplots(figsize=(6, 4.5))
        for d in (50, 200, 1000):  # courbes de référence
            ax.plot(phis * 100, kozeny_carman(phis, d * 1e-6) / M2_PAR_MD, alpha=0.4, label=f"d = {d} µm")
        ax.plot(phis * 100, kozeny_carman(phis, d_um * 1e-6) / M2_PAR_MD,
                color="black", label=f"d = {d_um} µm (choisi)")
        ax.plot(phi_kc * 100, k / M2_PAR_MD, "ro")
        ax.set_yscale("log")
        ax.set_xlabel("Porosité (%)")
        ax.set_ylabel("Perméabilité (mD)")
        ax.grid(alpha=0.3, which="both")
        ax.legend()
        st.pyplot(fig)

    st.caption(
        "k varie comme d² : doubler la taille des grains multiplie k par 4. "
        "Modèle valable pour des sables propres ; il ne s'applique pas aux roches "
        "argileuses, cimentées ou fracturées."
    )

# ---------------------------------------------------------------
# Onglet 5 : porosité de fracture
# ---------------------------------------------------------------
with tab5:
    st.latex(r"\phi_f \approx n \cdot \frac{e}{s} \qquad (e \ll s)")
    st.write(
        "e : ouverture d'une fracture ; s : espacement entre deux fractures d'une même famille ; "
        "n : nombre de familles de fractures (perpendiculaires entre elles)."
    )
    col_a, col_b = st.columns([1, 2])
    with col_a:
        e_mm = st.slider("Ouverture e (mm)", 0.01, 5.0, 0.2, 0.01)
        s = st.slider("Espacement s (m)", 0.05, 5.0, 0.5, 0.05)
        n_fam = st.radio("Familles de fractures", [1, 2, 3], index=1, horizontal=True)
        phi_mat = st.slider("Porosité de la matrice (%)", 0.0, 30.0, 5.0, 0.5) / 100

        e = e_mm / 1000
        phi_f = n_fam * e / s
        k_frac = e**3 / (12 * s)  # loi cubique, écoulement parallèle à une famille
        st.metric("Porosité de fracture", f"{phi_f * 100:.3f} %")
        st.metric("Porosité totale", f"{(phi_mat + phi_f) * 100:.2f} %")
        st.metric("Perméabilité due aux fractures", f"{k_frac / M2_PAR_MD:,.0f} mD")
        st.caption("Loi cubique : k = e³ / (12 s), écoulement parallèle aux fractures d'une famille.")

    with col_b:
        cote = 5  # côté du bloc (m)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor("tan")
        for x in np.arange(s / 2, cote, s):
            ax.axvline(x, color="steelblue", lw=1 + e_mm)
            if n_fam >= 2:
                ax.axhline(x, color="steelblue", lw=1 + e_mm)
        ax.set_xlim(0, cote)
        ax.set_ylim(0, cote)
        ax.set_aspect("equal")
        ax.set_xlabel("m")
        ax.set_ylabel("m")
        st.pyplot(fig)
        st.caption(
            "Bloc de 5 m × 5 m, ouvertures exagérées pour être visibles. "
            "La 3e famille, s'il y en a une, est perpendiculaire au plan de la figure."
        )

    st.info(
        "Règle simple : une mesure de porosité n'a de sens que sur un volume (VER) qui recoupe "
        f"au moins 10 à 20 fractures, soit un bloc de côté ≈ {10 * s:g} à {20 * s:g} m."
    )

# ---------------------------------------------------------------
# Onglet 6 : volume de pores d'un réservoir
# ---------------------------------------------------------------
with tab6:
    st.latex(r"V_{pores} = A \times h \times NTG \times \phi")
    st.write(
        "A : surface ; h : épaisseur brute ; NTG (net/gross) : proportion de roche réservoir ; "
        "φ : porosité efficace (matrice + fractures)."
    )
    col_a, col_b = st.columns([1, 2])
    with col_a:
        surface_km2 = st.number_input("Surface du réservoir (km²)", 0.1, 1000.0, 10.0, 0.5)
        epaisseur = st.number_input("Épaisseur brute (m)", 1.0, 1000.0, 50.0, 1.0)
        ntg = st.slider("Net/gross (NTG)", 0.1, 1.0, 0.8, 0.05)
        phi_res = st.slider("Porosité de la matrice (%)", 1.0, 40.0, 20.0, 0.5) / 100
        phi_frac = st.number_input("Porosité de fracture (%)", 0.0, 5.0, 0.0, 0.01) / 100
        sw = st.slider("Saturation en eau Sw", 0.0, 1.0, 0.3, 0.05)

    phi_tot = phi_res + phi_frac
    v_brut = surface_km2 * 1e6 * epaisseur  # m³
    v_pores = v_brut * ntg * phi_tot
    v_hc = v_pores * (1 - sw)

    with col_b:
        c1, c2 = st.columns(2)
        c1.metric("Volume brut", f"{v_brut / 1e6:,.1f} millions de m³")
        c1.metric("Volume de pores", f"{v_pores / 1e6:,.1f} millions de m³")
        c2.metric("Volume de pores", f"{v_pores * BBL_PAR_M3 / 1e6:,.0f} millions de barils")
        c2.metric("Volume d'hydrocarbures", f"{v_hc / 1e6:,.1f} millions de m³")

        parts = [
            ("Roche non réservoir", 1 - ntg, "lightgrey"),
            ("Matrice solide", ntg * (1 - phi_tot), "tan"),
            ("Eau", ntg * phi_tot * sw, "steelblue"),
            ("Hydrocarbures", ntg * phi_tot * (1 - sw), "darkorange"),
        ]
        fig, ax = plt.subplots(figsize=(7, 1.6))
        debut = 0
        for nom, part, couleur in parts:
            ax.barh([0], [part], left=[debut], color=couleur, label=f"{nom} ({part * 100:.1f} %)")
            debut += part
        ax.set_xlim(0, 1)
        ax.axis("off")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, frameon=False)
        st.pyplot(fig)

    st.caption("Volumes en conditions de réservoir (pas de conversion au volume de surface).")
