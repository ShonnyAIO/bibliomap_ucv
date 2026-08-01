from pathlib import Path
from typing import Optional
import sys

import pandas as pd
import streamlit as st


# ============================================================
# BiblioMap — MVP 1.0
# Interfaz inicial con identidad BiblioMap, BiblioIntel y LEGIN
# Conexión inicial con OpenAlex + Detalle geográfico + Mapa mundial
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
STYLES_DIR = ASSETS_DIR / "styles"
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"

# Permite importar módulos desde la carpeta raíz del proyecto.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.search_openalex import search_openalex, save_results
from modules.group_by_country import group_by_country, group_by_continent, save_geographic_outputs
from modules.generate_map import create_world_map, create_top_countries_bar
from modules.gap_suggester import (
    suggest_preliminary_gaps,
    save_gap_outputs,
    generate_extended_insights,
    save_extended_outputs,
)
from modules.generate_report import generate_report, generate_pdf_report
from modules.database import (
    initialize_db,
    get_users,
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    get_user_interests,
    add_user_interest,
    remove_user_interest,
    get_user_preferences,
    update_user_preference,
    get_notification_history,
    save_publications,
    get_publications
)
from modules.notifier import (
    send_notification_multichannel,
    process_whatsapp_queue,
    match_and_notify_users
)


LOGO_LEGIN = IMAGES_DIR / "logo_legin.png"
LOGO_BIBLIOMAP = IMAGES_DIR / "logo_bibliomap.png"
LOGO_BIBLIOINTEL = IMAGES_DIR / "logo_bibliointel.png"
LOGO_CEAP = IMAGES_DIR / "logo_ceap.png"
LOGO_FACES_UCV = IMAGES_DIR / "logo_faces_ucv.png"
LOGO_UCV = IMAGES_DIR / "logo_ucv.png"

CUSTOM_CSS = STYLES_DIR / "custom.css"

OPENALEX_RESULTS_PATH = PROCESSED_DIR / "openalex_search_results.csv"
GROUP_BY_COUNTRY_PATH = PROCESSED_DIR / "group_by_country.csv"
GROUP_BY_CONTINENT_PATH = PROCESSED_DIR / "group_by_continent.csv"
GAP_SUGGESTIONS_PATH = PROCESSED_DIR / "gap_suggestions.csv"
KEYWORD_SUMMARY_PATH = PROCESSED_DIR / "keyword_summary.csv"
TEMPORAL_SUMMARY_PATH = PROCESSED_DIR / "temporal_summary.csv"
TREND_SUMMARY_PATH = PROCESSED_DIR / "trend_summary.csv"
UNDERSTUDIED_AREAS_PATH = PROCESSED_DIR / "understudied_areas.csv"
RESEARCH_OPPORTUNITIES_PATH = PROCESSED_DIR / "research_opportunities.csv"

REPORT_MARKDOWN_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.md"
REPORT_HTML_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.html"
REPORT_PDF_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.pdf"

REFERENCE_NOTE = (
    "Desarrollo de LEGIN basado en el enfoque planteado en el artículo "
    "\"How to design bibliometric research: an overview and proposal\" "
    "de Oğuzhan Öztürk, Rıdvan Kocaman y Dominik K. Kanbach, "
    "Review of Managerial Science (2024) 18:3333–3361. "
    "https://doi.org/10.1007/s11846-024-00738-0"
)


def show_image(path: Path, width: Optional[int] = None, caption: Optional[str] = None) -> None:
    if path.exists():
        st.image(str(path), width=width, caption=caption)
    else:
        st.warning(f"No se encontró el archivo: {path.name}")


def load_css() -> None:
    if CUSTOM_CSS.exists():
        with open(CUSTOM_CSS, "r", encoding="utf-8") as css_file:
            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <style>
        /* Configuración de la barra superior y botón de menú móvil */
        header[data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.96) !important;
            backdrop-filter: blur(8px) !important;
            border-bottom: 1px solid #E6E6E6 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 3.5rem !important;
            z-index: 999990 !important;
            display: flex !important;
            align-items: center !important;
            pointer-events: auto !important;
        }

        div[data-testid="collapsedControl"],
        button[data-testid="stSidebarCollapseButton"],
        button[aria-label*="sidebar" i],
        button[aria-label*="Sidebar" i],
        [data-testid="stHeaderNav"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 1000000 !important;
            margin-left: 0.5rem !important;
            background-color: #0B2E59 !important;
            color: #FFFFFF !important;
            border-radius: 0.5rem !important;
            padding: 0.25rem 0.6rem !important;
            box-shadow: 0 2px 6px rgba(11, 46, 89, 0.3) !important;
            border: none !important;
        }

        div[data-testid="collapsedControl"] svg,
        button[data-testid="stSidebarCollapseButton"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
            stroke: #FFFFFF !important;
        }

        div[data-testid="stToolbar"] {
            display: none !important;
        }

        div[data-testid="stDecoration"] {
            display: none !important;
        }

        div[data-testid="stStatusWidget"] {
            display: none !important;
        }

        #MainMenu {
            visibility: hidden !important;
            display: none !important;
        }

        .reference-note {
            max-width: 980px;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
            font-size: 0.88rem;
            color: #444444;
            line-height: 1.45;
            margin-bottom: 1.5rem;
        }

        .geo-note {
            font-size: 0.88rem;
            color: #555555;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


MENU_OPTIONS = [
    "Inicio",
    "Buscar tema",
    "Mapa mundial",
    "Detalle geográfico",
    "Investigadores",
    "Publicaciones",
    "Brechas preliminares",
    "Reporte preliminar",
    "Usuarios y Notificaciones",
    "Aprender bibliometría",
]


def render_top_navigation() -> str:
    """Renders a responsive top navigation dropdown menu accessible directly on mobile/desktop."""
    current_page = st.session_state.get("current_page", "Inicio")
    current_idx = MENU_OPTIONS.index(current_page) if current_page in MENU_OPTIONS else 0

    st.markdown('<div class="mobile-top-nav" style="margin-bottom: 1rem;">', unsafe_allow_html=True)
    selected = st.selectbox(
        "🗺️ Menú de navegación por módulos",
        MENU_OPTIONS,
        index=current_idx,
        key="top_select_nav",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.current_page = selected
    return selected


def init_session_state() -> None:
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Inicio"

    if "openalex_results" not in st.session_state:
        st.session_state.openalex_results = pd.DataFrame()

    if "country_results" not in st.session_state:
        st.session_state.country_results = pd.DataFrame()

    if "continent_results" not in st.session_state:
        st.session_state.continent_results = pd.DataFrame()

    if "gap_results" not in st.session_state:
        st.session_state.gap_results = pd.DataFrame()

    if "keyword_results" not in st.session_state:
        st.session_state.keyword_results = pd.DataFrame()

    if "temporal_results" not in st.session_state:
        st.session_state.temporal_results = pd.DataFrame()

    if "trend_results" not in st.session_state:
        st.session_state.trend_results = pd.DataFrame()

    if "understudied_results" not in st.session_state:
        st.session_state.understudied_results = pd.DataFrame()

    if "opportunity_results" not in st.session_state:
        st.session_state.opportunity_results = pd.DataFrame()

    if "last_query_metadata" not in st.session_state:
        st.session_state.last_query_metadata = {}


def render_sidebar() -> str:
    with st.sidebar:
        show_image(LOGO_BIBLIOMAP, width=165)

        st.markdown("### BiblioMap")
        st.caption("Herramienta visual de orientación bibliométrica.")

        st.divider()

        st.markdown("#### Ecosistema")
        show_image(LOGO_BIBLIOINTEL, width=155)

        st.divider()

        st.markdown("#### Desarrollo de LEGIN")
        show_image(LOGO_LEGIN, width=125)
        st.caption("Laboratorio Estratégico de Gestión de la Innovación.")

        st.divider()

        current_page = st.session_state.get("current_page", "Inicio")
        current_idx = MENU_OPTIONS.index(current_page) if current_page in MENU_OPTIONS else 0

        selected = st.radio(
            "Navegación",
            MENU_OPTIONS,
            index=current_idx,
            key="sidebar_radio_nav",
        )
        st.session_state.current_page = selected

    return st.session_state.current_page


def render_header() -> None:
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        show_image(LOGO_BIBLIOMAP, width=320)

    st.markdown(
        f'<div class="reference-note">{REFERENCE_NOTE}</div>',
        unsafe_allow_html=True,
    )


def render_institutional_logos() -> None:
    st.divider()

    st.markdown("### Identidad institucional")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("#### Desarrollo de LEGIN")
        show_image(LOGO_LEGIN, width=145)
        st.caption("LEGIN")

    with col2:
        st.markdown("#### Entidades vinculadas")
        c1, c2, c3 = st.columns(3)

        with c1:
            show_image(LOGO_CEAP, width=125)
            st.markdown('<div class="small-caption">CEAP</div>', unsafe_allow_html=True)

        with c2:
            show_image(LOGO_FACES_UCV, width=145)
            st.markdown('<div class="small-caption">FACES UCV</div>', unsafe_allow_html=True)

        with c3:
            show_image(LOGO_UCV, width=115)
            st.markdown('<div class="small-caption">UCV</div>', unsafe_allow_html=True)


def page_inicio() -> None:
    render_header()

    st.markdown("## Bienvenido a BiblioMap")

    st.write(
        """
        **BiblioMap** es una herramienta informática de orientación bibliométrica
        diseñada para ayudar a estudiantes, tesistas e investigadores a explorar la
        producción científica mundial relacionada con un tema de investigación.
        """
    )

    st.write(
        """
        Su propósito es facilitar una primera aproximación a países, instituciones,
        autores, publicaciones y posibles brechas preliminares de investigación,
        usando fuentes académicas abiertas.
        """
    )

    st.info(
        """
        Los resultados de BiblioMap son orientadores, no conclusiones definitivas.
        La cobertura depende de la fuente consultada, los metadatos disponibles,
        los términos de búsqueda y el periodo seleccionado.
        """
    )

    st.markdown("## Ecosistema BiblioIntel")

    col1, col2 = st.columns([1, 2])

    with col1:
        show_image(LOGO_BIBLIOINTEL, width=310)

    with col2:
        st.write(
            """
            **BiblioIntel** significa **BIBLIOMETRÓLOGO INTELIGENTIZADOR**.
            Es el ecosistema conceptual y tecnológico que enmarca a BiblioMap.
            """
        )

        st.write(
            """
            BiblioMap es la primera herramienta visual y educativa del ecosistema,
            orientada al mapeo científico, la identificación de actores académicos
            y la detección preliminar de brechas de investigación.
            """
        )

    st.markdown("## Fórmula rectora")

    st.markdown(
        """
        - Humano define sentido.
        - Software procesa evidencia.
        - IA amplifica interpretación.
        - Inteligencia Humana profundiza el conocimiento.
        - IA + IH creaduccen.
        - La creatividad transforma resultados en conocimiento nuevo.
        """
    )

    render_institutional_logos()


def render_results_summary(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No se recuperaron resultados para esta búsqueda.")
        return

    total_records = len(df)
    total_citations = (
        int(df["cited_by_count"].fillna(0).sum())
        if "cited_by_count" in df.columns
        else 0
    )
    years = (
        df["publication_year"].dropna()
        if "publication_year" in df.columns
        else pd.Series(dtype=int)
    )
    countries_count = 0

    if "countries" in df.columns:
        country_values = []
        for item in df["countries"].dropna():
            country_values.extend(
                [country.strip() for country in str(item).split(";") if country.strip()]
            )
        countries_count = len(set(country_values))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Registros recuperados", total_records)

    with col2:
        st.metric("Citas acumuladas", total_citations)

    with col3:
        st.metric("Países detectados", countries_count)

    if not years.empty:
        st.caption(f"Rango de años recuperado: {int(years.min())}–{int(years.max())}")


def build_and_store_geographic_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    country_df = group_by_country(df)
    continent_df = group_by_continent(df)

    st.session_state.country_results = country_df
    st.session_state.continent_results = continent_df

    save_geographic_outputs(country_df, continent_df, str(PROCESSED_DIR))

    return country_df, continent_df


def load_geographic_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame]:
    country_df = pd.DataFrame()
    continent_df = pd.DataFrame()

    if GROUP_BY_COUNTRY_PATH.exists():
        country_df = pd.read_csv(GROUP_BY_COUNTRY_PATH)

    if GROUP_BY_CONTINENT_PATH.exists():
        continent_df = pd.read_csv(GROUP_BY_CONTINENT_PATH)

    if not country_df.empty:
        st.session_state.country_results = country_df

    if not continent_df.empty:
        st.session_state.continent_results = continent_df

    return country_df, continent_df


def get_country_results() -> pd.DataFrame:
    country_df = st.session_state.country_results

    if country_df.empty:
        country_df, _ = load_geographic_outputs_from_disk()

    return country_df


def _run_full_pipeline(df: pd.DataFrame, tema: str, query: str, year_from: int, year_to: int) -> None:
    """
    Ejecuta el pipeline completo de análisis bibliométrico sobre un DataFrame de resultados
    de OpenAlex: guarda CSV, genera agrupaciones geográficas, brechas, tendencias y
    dispara notificaciones a investigadores por coincidencia de intereses.

    Args:
        df: DataFrame con columnas estándar de OpenAlex.
        tema: Descripción del tema (para metadatos).
        query: Cadena de búsqueda usada (para metadatos).
        year_from: Año de inicio del rango de publicaciones.
        year_to: Año de fin del rango de publicaciones.
    """
    st.session_state.openalex_results = df
    st.session_state.last_query_metadata = {
        "tema": tema,
        "query": query,
        "year_from": year_from,
        "year_to": year_to,
        "source": "OpenAlex",
    }

    output_path = PROCESSED_DIR / "openalex_search_results.csv"
    save_results(df, output_path)
    st.caption(f"✅ Archivo guardado en: {output_path}")

    with st.spinner("Cargando resultados en la base de datos DuckDB..."):
        save_publications(df, tema=tema, query=query)
    st.caption("✅ Resultados cargados en base de datos local.")

    with st.spinner("Generando agrupaciones geográficas..."):
        country_df, continent_df = build_and_store_geographic_outputs(df)
    st.caption("✅ Agrupaciones geográficas generadas.")

    with st.spinner("Detectando brechas preliminares y términos frecuentes..."):
        gap_df, keyword_df, temporal_df = suggest_preliminary_gaps(
            df,
            country_df=country_df,
            continent_df=continent_df,
        )
        save_gap_outputs(gap_df, keyword_df, temporal_df, output_dir=PROCESSED_DIR)

    st.session_state.gap_results = gap_df
    st.session_state.keyword_results = keyword_df
    st.session_state.temporal_results = temporal_df
    st.caption("✅ Brechas y términos procesados.")

    with st.spinner("Calculando tendencias, áreas poco visibles y oportunidades..."):
        trend_df, understudied_df, opportunity_df = generate_extended_insights(
            df,
            gap_df=gap_df,
            keyword_df=keyword_df,
            temporal_df=temporal_df,
            country_df=country_df,
            continent_df=continent_df,
        )
        save_extended_outputs(trend_df, understudied_df, opportunity_df, output_dir=PROCESSED_DIR)

    st.session_state.trend_results = trend_df
    st.session_state.understudied_results = understudied_df
    st.session_state.opportunity_results = opportunity_df
    st.caption("✅ Tendencias y oportunidades calculadas.")

    with st.spinner("Comparando con intereses de investigadores y enviando alertas..."):
        reports = match_and_notify_users(df)

    if reports:
        st.info(f"📢 Se dispararon {len(reports)} alertas de artículos de interés a los investigadores.")
        with st.expander("Ver detalle de alertas enviadas", expanded=False):
            for r in reports:
                canales_str = ", ".join(
                    f"{canal}: {status}" for canal, status in r["canales"].items()
                ) or "Sin canales activos"
                st.caption(
                    f"**{r['usuario']}** | Interés: *{r['interes']}* | "
                    f"Artículo: '{r['articulo']}' | Canales: {canales_str}"
                )
    else:
        st.info("ℹ️ No se encontraron coincidencias entre los artículos y los intereses registrados, "
                "o los investigadores aún no tienen canales de notificación activos.")


def page_buscar_tema() -> None:
    st.markdown("## Buscar tema")

    st.write(
        """
        Introduce un tema o conjunto de palabras clave, o carga directamente un CSV
        exportado desde OpenAlex. BiblioMap procesará los metadatos bibliométricos
        y ejecutará el análisis completo, incluyendo notificaciones a investigadores.
        """
    )

    tab_buscar, tab_csv = st.tabs(["🔍 Buscar en OpenAlex", "📂 Cargar CSV de OpenAlex"])

    # ─────────────────────────────────────────────
    # TAB 1: Búsqueda en vivo en OpenAlex
    # ─────────────────────────────────────────────
    with tab_buscar:
        with st.form("search_form"):
            tema = st.text_input(
                "Tema de investigación",
                value="inteligencia artificial y creatividad científica",
            )

            palabras_clave = st.text_input(
                "Palabras clave para búsqueda en OpenAlex",
                value="artificial intelligence scientific creativity knowledge production",
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                year_from = st.number_input(
                    "Año inicial",
                    min_value=1900,
                    max_value=2100,
                    value=2015,
                )

            with col2:
                year_to = st.number_input(
                    "Año final",
                    min_value=1900,
                    max_value=2100,
                    value=2026,
                )

            with col3:
                max_results = st.number_input(
                    "Máximo de resultados",
                    min_value=10,
                    max_value=500,
                    value=50,
                    step=10,
                )

            submitted = st.form_submit_button("Buscar en OpenAlex")

        if submitted:
            query = palabras_clave.strip() or tema.strip()

            if not query:
                st.error("Debes introducir un tema o palabras clave.")
            else:
                try:
                    with st.spinner("Consultando OpenAlex y recuperando evidencia bibliométrica..."):
                        df = search_openalex(
                            query=query,
                            year_from=int(year_from),
                            year_to=int(year_to),
                            max_results=int(max_results),
                        )

                    st.success(f"Consulta completada. Registros recuperados: {len(df)}")
                    _run_full_pipeline(df, tema=tema, query=query, year_from=int(year_from), year_to=int(year_to))

                except Exception as error:
                    st.error("Ocurrió un error al consultar OpenAlex.")
                    st.exception(error)

        df_current = st.session_state.openalex_results

        if not df_current.empty:
            st.divider()
            st.markdown("## Resultados preliminares")

            render_results_summary(df_current)

            display_columns = [
                "title",
                "publication_year",
                "authors",
                "countries",
                "institutions",
                "source",
                "cited_by_count",
                "doi",
                "landing_page_url",
            ]

            available_columns = [
                column for column in display_columns if column in df_current.columns
            ]

            st.dataframe(
                df_current[available_columns],
                use_container_width=True,
                height=420,
            )

            csv_data = df_current.to_csv(index=False, encoding="utf-8-sig")

            st.download_button(
                label="Descargar resultados CSV",
                data=csv_data,
                file_name="openalex_search_results.csv",
                mime="text/csv",
            )

            st.info(
                """
                Estos resultados son preliminares. La interpretación final corresponde al investigador humano.
                El siguiente desarrollo organizará estos registros por país, institución, autores y publicaciones.
                """
            )

    # ─────────────────────────────────────────────
    # TAB 2: Carga de CSV exportado desde OpenAlex
    # ─────────────────────────────────────────────
    with tab_csv:
        st.markdown("### Importar resultados desde un archivo CSV de OpenAlex")

        st.write(
            """
            Carga un archivo CSV previamente exportado desde OpenAlex (o generado por
            BiblioMap en una sesión anterior). El sistema procesará los datos, los
            registrará en la base de datos y enviará alertas automáticas a los
            investigadores cuyos intereses coincidan con los artículos del archivo.
            """
        )

        st.info(
            "**Columnas requeridas:** `title`, `doi`, `publication_year`, `authors`, "
            "`countries`, `institutions`, `source`, `landing_page_url`, `abstract`, `keywords`. "
            "Las columnas faltantes serán rellenadas con valores vacíos."
        )

        uploaded_file = st.file_uploader(
            "Selecciona el archivo CSV de OpenAlex",
            type=["csv"],
            key="csv_uploader",
            help="Sube el archivo openalex_search_results.csv exportado desde BiblioMap o desde OpenAlex.",
        )

        if uploaded_file is not None:
            try:
                df_csv = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df_csv = pd.read_csv(uploaded_file, encoding="latin-1")
                except Exception as read_err:
                    st.error(f"No se pudo leer el archivo: {read_err}")
                    df_csv = pd.DataFrame()

            if not df_csv.empty:
                st.success(f"✅ Archivo cargado: **{uploaded_file.name}** | {len(df_csv)} registros, {len(df_csv.columns)} columnas.")

                # ── Columnas detectadas ──────────────────────
                required_cols = [
                    "title", "doi", "publication_year", "publication_date",
                    "type", "cited_by_count", "authors", "institutions",
                    "countries", "source", "landing_page_url",
                    "is_open_access", "abstract", "keywords",
                ]
                missing_cols = [c for c in required_cols if c not in df_csv.columns]
                if missing_cols:
                    st.warning(
                        f"Las siguientes columnas no están en el CSV y se rellenarán con valores vacíos: "
                        f"`{'`, `'.join(missing_cols)}`"
                    )
                    for col in missing_cols:
                        df_csv[col] = ""

                # ── Vista previa ─────────────────────────────
                with st.expander("Vista previa del CSV (primeras 10 filas)", expanded=True):
                    preview_cols = [c for c in ["title", "publication_year", "authors", "countries", "source", "keywords"] if c in df_csv.columns]
                    st.dataframe(df_csv[preview_cols].head(10), use_container_width=True)

                # ── Metadatos opcionales del tema ─────────────
                st.markdown("#### Descripción del tema (opcional)")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    csv_tema = st.text_input(
                        "Tema de investigación",
                        value="Importado desde CSV",
                        key="csv_tema",
                    )
                with col_m2:
                    csv_query = st.text_input(
                        "Consulta / palabras clave del CSV",
                        value=uploaded_file.name.replace(".csv", ""),
                        key="csv_query",
                    )
                with col_m3:
                    years_detected = []
                    if "publication_year" in df_csv.columns:
                        years_detected = pd.to_numeric(df_csv["publication_year"], errors="coerce").dropna().astype(int).tolist()
                    csv_year_from = int(min(years_detected)) if years_detected else 2000
                    csv_year_to = int(max(years_detected)) if years_detected else 2026
                    st.metric("Rango de años detectado", f"{csv_year_from} – {csv_year_to}")

                st.divider()

                # ── Botón de procesamiento ───────────────────
                if st.button(
                    "🚀 Procesar CSV: cargar a BD, analizar y notificar",
                    type="primary",
                    key="btn_process_csv",
                ):
                    with st.spinner("Ejecutando pipeline completo de análisis bibliométrico..."):
                        _run_full_pipeline(
                            df_csv,
                            tema=csv_tema,
                            query=csv_query,
                            year_from=csv_year_from,
                            year_to=csv_year_to,
                        )

                    st.success(
                        f"✅ Pipeline completado. {len(df_csv)} registros procesados desde **{uploaded_file.name}**."
                    )

                    st.markdown("---")
                    st.markdown("#### Resultados del CSV procesado")

                    render_results_summary(df_csv)

                    available_preview = [
                        c for c in ["title", "publication_year", "authors", "countries", "source", "cited_by_count", "doi"] if c in df_csv.columns
                    ]
                    st.dataframe(df_csv[available_preview], use_container_width=True, height=380)

                    st.download_button(
                        label="Descargar CSV normalizado",
                        data=df_csv.to_csv(index=False, encoding="utf-8-sig"),
                        file_name="openalex_search_results.csv",
                        mime="text/csv",
                    )

        else:
            st.markdown(
                """
                **¿Cómo obtener el CSV?**
                1. Realiza una búsqueda en la pestaña **"🔍 Buscar en OpenAlex"**.
                2. Descarga el archivo usando el botón **"Descargar resultados CSV"**.
                3. O usa el archivo `openalex_search_results.csv` que ya tienes guardado.
                4. También puedes exportar directamente desde [OpenAlex.org](https://openalex.org).
                """
            )




def page_mapa_mundial() -> None:
    st.markdown("## Mapa mundial")

    st.write(
        """
        Visualización geográfica preliminar de la producción científica recuperada.
        El mapa usa la agrupación por país generada desde los metadatos de OpenAlex.
        """
    )

    country_df = get_country_results()

    if country_df.empty:
        st.warning("Todavía no hay datos para el mapa. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    metric_label = st.selectbox(
        "Métrica del mapa",
        options=["Publicaciones", "Citas acumuladas"],
        index=0,
    )

    metric = "publications" if metric_label == "Publicaciones" else "cited_by_count"

    fig_map = create_world_map(country_df, metric=metric)
    st.plotly_chart(fig_map, use_container_width=True)

    st.caption(
        "Nota: una publicación puede aparecer asociada a más de un país si tiene afiliaciones multinacionales."
    )

    st.divider()

    top_n = st.slider("Número de países en el ranking", min_value=5, max_value=30, value=15, step=5)

    fig_bar = create_top_countries_bar(country_df, metric=metric, top_n=top_n)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.info(
        """
        Este mapa es una visualización exploratoria. No debe interpretarse como cobertura absoluta del campo,
        sino como una lectura preliminar dependiente de OpenAlex, de los términos de búsqueda y de los metadatos disponibles.
        """
    )


def page_detalle_geografico() -> None:
    st.markdown("## Detalle geográfico")

    st.write(
        """
        Esta sección organiza los resultados recuperados desde OpenAlex por país y por continente o región amplia.
        Permite observar la distribución preliminar de la producción científica asociada al tema consultado.
        """
    )

    country_df = st.session_state.country_results
    continent_df = st.session_state.continent_results

    if country_df.empty or continent_df.empty:
        country_df, continent_df = load_geographic_outputs_from_disk()

    if country_df.empty or continent_df.empty:
        st.warning("Todavía no hay datos geográficos. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    total_countries = (
        len(country_df[country_df["country_code"] != "Unknown"])
        if "country_code" in country_df.columns
        else len(country_df)
    )
    total_publications_country = int(country_df["publications"].sum()) if "publications" in country_df.columns else 0
    total_citations_country = int(country_df["cited_by_count"].sum()) if "cited_by_count" in country_df.columns else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Países detectados", total_countries)

    with col2:
        st.metric("Apariciones país-publicación", total_publications_country)

    with col3:
        st.metric("Citas acumuladas por país", total_citations_country)

    st.caption(
        "Nota: una misma publicación puede aparecer en más de un país si tiene autorías o afiliaciones multinacionales."
    )

    st.divider()

    st.markdown("### Distribución por continente o región")

    continent_columns = [
        "continent",
        "publications",
        "cited_by_count",
        "countries",
    ]
    continent_available = [column for column in continent_columns if column in continent_df.columns]

    st.dataframe(
        continent_df[continent_available],
        use_container_width=True,
        height=260,
    )

    continent_csv = continent_df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="Descargar agrupación por continente CSV",
        data=continent_csv,
        file_name="group_by_continent.csv",
        mime="text/csv",
    )

    st.divider()

    st.markdown("### Distribución por país")

    country_columns = [
        "country_code",
        "country",
        "continent",
        "publications",
        "cited_by_count",
        "institutions",
        "authors",
    ]
    country_available = [column for column in country_columns if column in country_df.columns]

    st.dataframe(
        country_df[country_available],
        use_container_width=True,
        height=520,
    )

    country_csv = country_df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="Descargar agrupación por país CSV",
        data=country_csv,
        file_name="group_by_country.csv",
        mime="text/csv",
    )

    st.info(
        """
        Interpretación preliminar: esta tabla permite identificar concentración geográfica,
        regiones activas y posibles espacios de baja presencia bibliométrica. No debe asumirse
        que la ausencia de registros equivale a inexistencia de investigación; depende de la fuente,
        los metadatos y los términos de búsqueda.
        """
    )


def page_publicaciones() -> None:
    st.markdown("## Publicaciones en Base de Datos")
    st.write(
        """
        Visualiza todas las publicaciones científicas que han sido recuperadas de OpenAlex
        o cargadas vía CSV, y almacenadas de forma persistente en la base de datos DuckDB.
        """
    )

    df_db = get_publications()

    if df_db.empty:
        st.info("No hay publicaciones registradas de forma persistente en la base de datos local.")
        st.write("Realiza una búsqueda o carga un CSV en la sección **Buscar tema** para poblar la base de datos.")
        return

    st.success(f"📂 Se encontraron **{len(df_db)}** publicaciones registradas en la base de datos local.")

    # Filtro por tema de investigación
    temas = ["Todas"] + sorted([str(t) for t in df_db["tema"].unique() if t and str(t).strip() != "nan"])
    selected_tema = st.selectbox("Filtrar por Tema de Investigación", temas)

    if selected_tema != "Todas":
        df_display = df_db[df_db["tema"] == selected_tema]
    else:
        df_display = df_db

    display_columns = [
        "title",
        "publication_year",
        "authors",
        "source",
        "doi",
        "landing_page_url",
        "tema",
        "creado_en"
    ]

    available_columns = [column for column in display_columns if column in df_display.columns]

    st.dataframe(
        df_display[available_columns],
        use_container_width=True,
        height=500,
    )



def page_investigadores() -> None:
    st.markdown("## Investigadores")

    df = st.session_state.openalex_results

    if df.empty and OPENALEX_RESULTS_PATH.exists():
        df = pd.read_csv(OPENALEX_RESULTS_PATH)
        st.session_state.openalex_results = df

    if df.empty:
        st.warning("Todavía no hay resultados. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    authors_rows = []

    for _, row in df.iterrows():
        authors_raw = str(row.get("authors", "") or "")
        title = row.get("title", "")
        year = row.get("publication_year", "")
        countries = row.get("countries", "")
        institutions = row.get("institutions", "")

        for author in [item.strip() for item in authors_raw.split(";") if item.strip()]:
            authors_rows.append(
                {
                    "author": author,
                    "publication_year": year,
                    "title": title,
                    "countries": countries,
                    "institutions": institutions,
                }
            )

    authors_df = pd.DataFrame(authors_rows)

    if authors_df.empty:
        st.warning("No se detectaron autores en los metadatos recuperados.")
        return

    summary_df = (
        authors_df.groupby("author", as_index=False)
        .agg(
            publications=("title", "count"),
            countries=(
                "countries",
                lambda values: "; ".join(
                    sorted(
                        {
                            item.strip()
                            for value in values
                            for item in str(value).split(";")
                            if item.strip()
                        }
                    )
                ),
            ),
            institutions=(
                "institutions",
                lambda values: "; ".join(
                    sorted(
                        {
                            item.strip()
                            for value in values
                            for item in str(value).split(";")
                            if item.strip()
                        }
                    )
                ),
            ),
        )
        .sort_values("publications", ascending=False)
    )

    st.dataframe(summary_df, use_container_width=True, height=500)


def load_gap_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga salidas de brechas desde data/processed si existen.
    """
    gap_df = pd.DataFrame()
    keyword_df = pd.DataFrame()
    temporal_df = pd.DataFrame()

    if GAP_SUGGESTIONS_PATH.exists():
        gap_df = pd.read_csv(GAP_SUGGESTIONS_PATH)

    if KEYWORD_SUMMARY_PATH.exists():
        keyword_df = pd.read_csv(KEYWORD_SUMMARY_PATH)

    if TEMPORAL_SUMMARY_PATH.exists():
        temporal_df = pd.read_csv(TEMPORAL_SUMMARY_PATH)

    if not gap_df.empty:
        st.session_state.gap_results = gap_df

    if not keyword_df.empty:
        st.session_state.keyword_results = keyword_df

    if not temporal_df.empty:
        st.session_state.temporal_results = temporal_df

    return gap_df, keyword_df, temporal_df


def load_extended_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga tendencias, áreas poco visibles y oportunidades desde data/processed si existen.
    """
    trend_df = pd.DataFrame()
    understudied_df = pd.DataFrame()
    opportunity_df = pd.DataFrame()

    if TREND_SUMMARY_PATH.exists():
        trend_df = pd.read_csv(TREND_SUMMARY_PATH)

    if UNDERSTUDIED_AREAS_PATH.exists():
        understudied_df = pd.read_csv(UNDERSTUDIED_AREAS_PATH)

    if RESEARCH_OPPORTUNITIES_PATH.exists():
        opportunity_df = pd.read_csv(RESEARCH_OPPORTUNITIES_PATH)

    if not trend_df.empty:
        st.session_state.trend_results = trend_df

    if not understudied_df.empty:
        st.session_state.understudied_results = understudied_df

    if not opportunity_df.empty:
        st.session_state.opportunity_results = opportunity_df

    return trend_df, understudied_df, opportunity_df


def page_brechas_preliminares() -> None:
    """
    Muestra brechas preliminares, tendencias, áreas poco visibles y oportunidades.
    """
    st.markdown("## Brechas preliminares")

    st.write(
        """
        Esta sección presenta señales orientadoras de posibles brechas de investigación.
        No son conclusiones definitivas: deben ser revisadas, contrastadas y validadas
        por el investigador humano.
        """
    )

    gap_df = st.session_state.gap_results
    keyword_df = st.session_state.keyword_results
    temporal_df = st.session_state.temporal_results
    trend_df = st.session_state.trend_results
    understudied_df = st.session_state.understudied_results
    opportunity_df = st.session_state.opportunity_results

    if gap_df.empty or keyword_df.empty or temporal_df.empty:
        gap_df, keyword_df, temporal_df = load_gap_outputs_from_disk()

    if trend_df.empty or understudied_df.empty or opportunity_df.empty:
        trend_df, understudied_df, opportunity_df = load_extended_outputs_from_disk()

    if gap_df.empty:
        st.warning(
            "Todavía no hay sugerencias de brechas. Primero realiza una búsqueda en la sección 'Buscar tema' o ejecuta py modules/gap_suggester.py."
        )
        return

    for column in ["dimension", "signal", "evidence", "suggested_gap", "caution", "priority"]:
        if column not in gap_df.columns:
            gap_df[column] = ""

    gap_df = gap_df.fillna("")
    gap_df["dimension"] = gap_df["dimension"].astype(str)
    gap_df["priority"] = gap_df["priority"].astype(str)

    total_gaps = len(gap_df)
    high_priority = len(gap_df[gap_df["priority"].str.lower() == "alta"])
    dimensions = gap_df["dimension"].nunique()
    total_trends = len(trend_df) if trend_df is not None else 0
    total_understudied = len(understudied_df) if understudied_df is not None else 0
    total_opportunities = len(opportunity_df) if opportunity_df is not None else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Señales de brecha", total_gaps)

    with col2:
        st.metric("Prioridad alta", high_priority)

    with col3:
        st.metric("Tendencias", total_trends)

    with col4:
        st.metric("Oportunidades", total_opportunities)

    st.divider()

    st.markdown("### Filtros de lectura")

    filter_col1, filter_col2 = st.columns(2)

    dimension_options = sorted([value for value in gap_df["dimension"].unique().tolist() if value])
    priority_order = ["Alta", "Media", "Baja"]
    priority_options = [
        priority for priority in priority_order
        if priority in gap_df["priority"].unique().tolist()
    ]
    extra_priorities = sorted(
        [
            priority for priority in gap_df["priority"].unique().tolist()
            if priority and priority not in priority_options
        ]
    )
    priority_options.extend(extra_priorities)

    with filter_col1:
        selected_dimensions = st.multiselect(
            "Filtrar por dimensión",
            options=dimension_options,
            default=dimension_options,
        )

    with filter_col2:
        selected_priorities = st.multiselect(
            "Filtrar por prioridad",
            options=priority_options,
            default=priority_options,
        )

    filtered_df = gap_df[
        gap_df["dimension"].isin(selected_dimensions)
        & gap_df["priority"].isin(selected_priorities)
    ].copy()

    st.caption(
        f"Mostrando {len(filtered_df)} de {len(gap_df)} señales preliminares."
    )

    if filtered_df.empty:
        st.warning("No hay brechas que coincidan con los filtros seleccionados.")
        return

    st.divider()

    main_tabs = st.tabs(
        [
            "Brechas",
            "Tendencias de estudio",
            "Áreas poco visibles",
            "Oportunidades investigativas",
            "Términos y temporalidad",
        ]
    )

    with main_tabs[0]:
        st.markdown("### Resumen visual de brechas")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            dimension_counts = (
                filtered_df.groupby("dimension", as_index=False)
                .size()
                .rename(columns={"size": "señales"})
                .sort_values("señales", ascending=False)
            )

            if not dimension_counts.empty:
                st.markdown("**Señales por dimensión**")
                st.bar_chart(
                    dimension_counts.set_index("dimension")["señales"]
                )

        with chart_col2:
            priority_counts = (
                filtered_df.groupby("priority", as_index=False)
                .size()
                .rename(columns={"size": "señales"})
                .sort_values("señales", ascending=False)
            )

            if not priority_counts.empty:
                st.markdown("**Señales por prioridad**")
                st.bar_chart(
                    priority_counts.set_index("priority")["señales"]
                )

        st.divider()

        st.markdown("### Lectura interpretativa por tarjetas")

        priority_icon = {
            "Alta": "🔴",
            "Media": "🟠",
            "Baja": "🟢",
        }

        for index, row in filtered_df.reset_index(drop=True).iterrows():
            priority = str(row.get("priority", "")).strip()
            dimension = str(row.get("dimension", "")).strip()
            signal = str(row.get("signal", "")).strip()
            evidence = str(row.get("evidence", "")).strip()
            suggested_gap = str(row.get("suggested_gap", "")).strip()
            caution = str(row.get("caution", "")).strip()

            icon = priority_icon.get(priority, "⚪")
            expander_title = f"{icon} {dimension} — {signal}"

            with st.expander(expander_title, expanded=(index < 3)):
                st.markdown(f"**Prioridad:** {priority or 'No indicada'}")
                st.markdown("**Señal detectada:**")
                st.write(signal or "No indicada.")

                st.markdown("**Evidencia bibliométrica usada por BiblioMap:**")
                st.write(evidence or "No disponible.")

                st.markdown("**Brecha preliminar sugerida:**")
                st.write(suggested_gap or "No disponible.")

                st.markdown("**Cautela metodológica:**")
                st.warning(caution or "Debe validarse mediante lectura crítica y contraste con otras fuentes.")

        st.divider()

        st.markdown("### Tabla técnica de brechas")

        with st.expander("Ver tabla completa de brechas preliminares", expanded=False):
            display_columns = [
                "dimension",
                "signal",
                "evidence",
                "suggested_gap",
                "caution",
                "priority",
            ]

            available_columns = [column for column in display_columns if column in filtered_df.columns]

            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True,
                height=420,
            )

        st.download_button(
            label="Descargar brechas filtradas CSV",
            data=filtered_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="gap_suggestions_filtered.csv",
            mime="text/csv",
        )

        st.download_button(
            label="Descargar todas las brechas CSV",
            data=gap_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="gap_suggestions.csv",
            mime="text/csv",
        )

    with main_tabs[1]:
        st.markdown("### Tendencias de estudio detectadas")

        st.write(
            """
            Esta sección resume líneas dominantes, señales emergentes, señales temporales
            y polos visibles dentro de la muestra recuperada.
            """
        )

        if trend_df is None or trend_df.empty:
            st.warning("No hay tendencias disponibles. Ejecuta nuevamente la búsqueda o py modules/gap_suggester.py.")
        else:
            trend_df = trend_df.fillna("")

            for column in [
                "trend_type",
                "trend",
                "evidence",
                "period_signal",
                "associated_terms",
                "interpretation",
                "suggested_use",
                "caution",
                "strength",
            ]:
                if column not in trend_df.columns:
                    trend_df[column] = ""

            type_options = sorted([value for value in trend_df["trend_type"].astype(str).unique().tolist() if value])

            selected_types = st.multiselect(
                "Filtrar tendencias por tipo",
                options=type_options,
                default=type_options,
            )

            trend_filtered = trend_df[trend_df["trend_type"].astype(str).isin(selected_types)].copy()

            for index, row in trend_filtered.reset_index(drop=True).iterrows():
                trend_type = str(row.get("trend_type", "")).strip()
                trend = str(row.get("trend", "")).strip()
                strength = str(row.get("strength", "")).strip()

                with st.expander(f"📈 {trend_type} — {trend} [{strength}]", expanded=(index < 2)):
                    st.markdown("**Evidencia:**")
                    st.write(row.get("evidence", ""))

                    st.markdown("**Señal temporal o contextual:**")
                    st.write(row.get("period_signal", ""))

                    st.markdown("**Términos asociados:**")
                    st.write(row.get("associated_terms", ""))

                    st.markdown("**Interpretación preliminar:**")
                    st.write(row.get("interpretation", ""))

                    st.markdown("**Uso sugerido:**")
                    st.write(row.get("suggested_use", ""))

                    st.markdown("**Cautela:**")
                    st.warning(row.get("caution", ""))

            with st.expander("Ver tabla técnica de tendencias", expanded=False):
                st.dataframe(trend_filtered, use_container_width=True, height=380)

            st.download_button(
                label="Descargar tendencias CSV",
                data=trend_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="trend_summary_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[2]:
        st.markdown("### Áreas poco estudiadas o poco visibles")

        st.write(
            """
            BiblioMap no afirma que un área no exista: indica si aparece poco o no aparece
            suficientemente en esta muestra, según una lista de dimensiones esperadas.
            """
        )

        if understudied_df is None or understudied_df.empty:
            st.warning("No hay áreas poco visibles disponibles. Ejecuta nuevamente la búsqueda o py modules/gap_suggester.py.")
        else:
            understudied_df = understudied_df.fillna("")

            for column in [
                "expected_dimension",
                "visibility_level",
                "matched_terms",
                "evidence",
                "possible_gap",
                "suggested_question",
                "how_to_verify",
                "caution",
            ]:
                if column not in understudied_df.columns:
                    understudied_df[column] = ""

            visibility_options = sorted([value for value in understudied_df["visibility_level"].astype(str).unique().tolist() if value])

            selected_visibility = st.multiselect(
                "Filtrar por nivel de visibilidad",
                options=visibility_options,
                default=visibility_options,
            )

            understudied_filtered = understudied_df[
                understudied_df["visibility_level"].astype(str).isin(selected_visibility)
            ].copy()

            visibility_counts = (
                understudied_filtered.groupby("visibility_level", as_index=False)
                .size()
                .rename(columns={"size": "áreas"})
            )

            if not visibility_counts.empty:
                st.markdown("**Áreas por nivel de visibilidad**")
                st.bar_chart(
                    visibility_counts.set_index("visibility_level")["áreas"]
                )

            for index, row in understudied_filtered.reset_index(drop=True).iterrows():
                dimension = str(row.get("expected_dimension", "")).strip()
                visibility = str(row.get("visibility_level", "")).strip()

                with st.expander(f"🔎 {dimension} — visibilidad: {visibility}", expanded=(index < 3)):
                    st.markdown("**Términos encontrados:**")
                    st.write(row.get("matched_terms", ""))

                    st.markdown("**Evidencia:**")
                    st.write(row.get("evidence", ""))

                    st.markdown("**Posible vacío:**")
                    st.write(row.get("possible_gap", ""))

                    st.markdown("**Pregunta de investigación sugerida:**")
                    st.success(row.get("suggested_question", ""))

                    st.markdown("**Cómo verificarlo:**")
                    st.write(row.get("how_to_verify", ""))

                    st.markdown("**Cautela:**")
                    st.warning(row.get("caution", ""))

            with st.expander("Ver tabla técnica de áreas poco visibles", expanded=False):
                st.dataframe(understudied_filtered, use_container_width=True, height=420)

            st.download_button(
                label="Descargar áreas poco visibles CSV",
                data=understudied_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="understudied_areas_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[3]:
        st.markdown("### Oportunidades investigativas")

        st.write(
            """
            Esta sección traduce señales de brecha, tendencias y áreas poco visibles
            en oportunidades preliminares de investigación.
            """
        )

        if opportunity_df is None or opportunity_df.empty:
            st.warning("No hay oportunidades disponibles. Ejecuta nuevamente la búsqueda o py modules/gap_suggester.py.")
        else:
            opportunity_df = opportunity_df.fillna("")

            for column in [
                "opportunity_type",
                "opportunity",
                "possible_research_question",
                "supporting_signal",
                "recommended_next_step",
                "priority",
            ]:
                if column not in opportunity_df.columns:
                    opportunity_df[column] = ""

            opportunity_priority_options = sorted([value for value in opportunity_df["priority"].astype(str).unique().tolist() if value])

            selected_opportunity_priorities = st.multiselect(
                "Filtrar oportunidades por prioridad",
                options=opportunity_priority_options,
                default=opportunity_priority_options,
            )

            opportunity_filtered = opportunity_df[
                opportunity_df["priority"].astype(str).isin(selected_opportunity_priorities)
            ].copy()

            for index, row in opportunity_filtered.reset_index(drop=True).iterrows():
                opportunity_type = str(row.get("opportunity_type", "")).strip()
                priority = str(row.get("priority", "")).strip()
                opportunity = str(row.get("opportunity", "")).strip()

                with st.expander(f"💡 {opportunity_type} — {priority}", expanded=(index < 3)):
                    st.markdown("**Oportunidad:**")
                    st.write(opportunity)

                    st.markdown("**Pregunta posible:**")
                    st.success(row.get("possible_research_question", ""))

                    st.markdown("**Señal que la respalda:**")
                    st.write(row.get("supporting_signal", ""))

                    st.markdown("**Siguiente paso recomendado:**")
                    st.write(row.get("recommended_next_step", ""))

            with st.expander("Ver tabla técnica de oportunidades", expanded=False):
                st.dataframe(opportunity_filtered, use_container_width=True, height=420)

            st.download_button(
                label="Descargar oportunidades CSV",
                data=opportunity_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="research_opportunities_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[4]:
        st.markdown("### Términos y patrones frecuentes")

        if not keyword_df.empty:
            keyword_df = keyword_df.fillna("")

            for column in ["keyword", "frequency", "type"]:
                if column not in keyword_df.columns:
                    keyword_df[column] = ""

            keyword_df["frequency"] = pd.to_numeric(
                keyword_df["frequency"],
                errors="coerce",
            ).fillna(0).astype(int)

            keyword_types = sorted([value for value in keyword_df["type"].astype(str).unique().tolist() if value])

            selected_keyword_types = st.multiselect(
                "Filtrar términos por tipo",
                options=keyword_types,
                default=keyword_types,
            )

            keyword_filtered = keyword_df[keyword_df["type"].astype(str).isin(selected_keyword_types)].copy()

            top_terms = (
                keyword_filtered.sort_values("frequency", ascending=False)
                .head(20)
            )

            if not top_terms.empty:
                st.markdown("**Ranking de términos y patrones**")
                st.bar_chart(
                    top_terms.set_index("keyword")["frequency"]
                )

            with st.expander("Ver tabla de términos frecuentes", expanded=False):
                keyword_columns = [
                    column for column in ["keyword", "frequency", "type"]
                    if column in keyword_filtered.columns
                ]

                st.dataframe(
                    keyword_filtered[keyword_columns],
                    use_container_width=True,
                    height=320,
                )

            st.download_button(
                label="Descargar términos frecuentes CSV",
                data=keyword_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="keyword_summary_filtered.csv",
                mime="text/csv",
            )
        else:
            st.warning("No hay términos frecuentes disponibles.")

        st.divider()

        st.markdown("### Serie temporal de publicaciones")

        if not temporal_df.empty:
            temporal_df = temporal_df.fillna("")

            for column in ["publication_year", "publications", "cited_by_count"]:
                if column not in temporal_df.columns:
                    temporal_df[column] = 0

            temporal_df["publication_year"] = pd.to_numeric(
                temporal_df["publication_year"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df["publications"] = pd.to_numeric(
                temporal_df["publications"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df["cited_by_count"] = pd.to_numeric(
                temporal_df["cited_by_count"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df = temporal_df[temporal_df["publication_year"] > 0].sort_values("publication_year")

            if not temporal_df.empty:
                chart_df = temporal_df.copy()
                chart_df["publication_year"] = chart_df["publication_year"].astype(str)

                st.markdown("**Publicaciones por año**")
                st.bar_chart(
                    chart_df.set_index("publication_year")["publications"]
                )

                with st.expander("Ver tabla temporal", expanded=False):
                    temporal_columns = [
                        column
                        for column in ["publication_year", "publications", "cited_by_count"]
                        if column in temporal_df.columns
                    ]

                    st.dataframe(
                        temporal_df[temporal_columns],
                        use_container_width=True,
                        height=280,
                    )

                st.download_button(
                    label="Descargar serie temporal CSV",
                    data=temporal_df.to_csv(index=False, encoding="utf-8-sig"),
                    file_name="temporal_summary.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No hay años válidos en la serie temporal.")
        else:
            st.warning("No hay serie temporal disponible.")

    st.info(
        """
        Estas salidas son preliminares. BiblioMap detecta señales a partir de metadatos,
        frecuencias, países, años, fuentes, autores e instituciones. La validación requiere
        lectura crítica, revisión metodológica y contraste con otras bases como Scopus,
        Web of Science, Dimensions, Lens, Google Scholar u otras fuentes pertinentes.
        """
    )


def page_reporte_preliminar() -> None:
    """
    Genera y muestra el reporte bibliométrico preliminar descargable.
    """
    st.markdown("## Reporte preliminar")

    st.write(
        """
        Esta sección genera un informe bibliométrico preliminar a partir de los resultados
        ya procesados por BiblioMap: búsqueda OpenAlex, agrupación geográfica, brechas,
        tendencias, áreas poco visibles y oportunidades investigativas.
        """
    )

    st.info(
        """
        El reporte es orientador. No sustituye una revisión sistemática ni una
        investigación bibliométrica completa. Sirve como primer documento de trabajo
        para lectura crítica, tutoría y delimitación del problema.
        """
    )

    metadata = st.session_state.get("last_query_metadata", {})
    tema = metadata.get("tema", "")
    query = metadata.get("query", "")
    year_from = metadata.get("year_from", "")
    year_to = metadata.get("year_to", "")
    source = metadata.get("source", "OpenAlex")

    report_query = tema or query or "Tema no especificado"

    st.markdown("### Datos base del reporte")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Fuente", source)

    with col2:
        st.metric("Año inicial", year_from if year_from else "N/D")

    with col3:
        st.metric("Año final", year_to if year_to else "N/D")

    with col4:
        processed_ready = OPENALEX_RESULTS_PATH.exists()
        st.metric("Datos procesados", "Sí" if processed_ready else "No")

    if query:
        st.caption(f"Consulta OpenAlex: {query}")

    st.divider()

    required_files = [
        ("Resultados OpenAlex", OPENALEX_RESULTS_PATH),
        ("Agrupación por país", GROUP_BY_COUNTRY_PATH),
        ("Agrupación por continente", GROUP_BY_CONTINENT_PATH),
        ("Brechas preliminares", GAP_SUGGESTIONS_PATH),
        ("Términos frecuentes", KEYWORD_SUMMARY_PATH),
        ("Serie temporal", TEMPORAL_SUMMARY_PATH),
        ("Tendencias", TREND_SUMMARY_PATH),
        ("Áreas poco visibles", UNDERSTUDIED_AREAS_PATH),
        ("Oportunidades investigativas", RESEARCH_OPPORTUNITIES_PATH),
    ]

    status_rows = []

    for label, path in required_files:
        status_rows.append(
            {
                "Elemento": label,
                "Estado": "Disponible" if path.exists() else "No encontrado",
                "Ruta": str(path.relative_to(BASE_DIR)) if path.exists() else str(path.relative_to(BASE_DIR)),
            }
        )

    status_df = pd.DataFrame(status_rows)

    with st.expander("Ver archivos usados para construir el reporte", expanded=False):
        st.dataframe(status_df, use_container_width=True, height=330)

    missing_files = [label for label, path in required_files if not path.exists()]

    if missing_files:
        st.warning(
            "Faltan algunos archivos procesados. El reporte puede generarse, pero quedará incompleto: "
            + ", ".join(missing_files)
        )

    col_btn1, col_btn2 = st.columns([1, 2])

    with col_btn1:
        generate_clicked = st.button("Generar / actualizar reporte", type="primary")

    with col_btn2:
        st.caption(
            "Recomendación: primero ejecuta una búsqueda en 'Buscar tema' y revisa brechas/tendencias antes de generar el reporte."
        )

    if generate_clicked:
        try:
            with st.spinner("Generando reporte bibliométrico preliminar..."):
                markdown_text, md_path, html_path = generate_report(query=report_query)
                pdf_path = generate_pdf_report(query=report_query)

            st.success("Reporte generado correctamente.")
            st.caption(f"Markdown: {md_path}")
            st.caption(f"HTML: {html_path}")
            st.caption(f"PDF: {pdf_path}")

        except Exception as error:
            st.error("Ocurrió un error al generar el reporte.")
            st.exception(error)

    st.divider()

    st.markdown("### Descargar reporte")

    report_exists = REPORT_MARKDOWN_PATH.exists() or REPORT_HTML_PATH.exists() or REPORT_PDF_PATH.exists()

    if not report_exists:
        st.warning("Todavía no hay reporte generado. Presiona 'Generar / actualizar reporte'.")
        render_footer()
        return

    download_col1, download_col2, download_col3 = st.columns(3)

    if REPORT_MARKDOWN_PATH.exists():
        markdown_text = REPORT_MARKDOWN_PATH.read_text(encoding="utf-8")

        with download_col1:
            st.download_button(
                label="Descargar reporte Markdown (.md)",
                data=markdown_text.encode("utf-8"),
                file_name="bibliomap_preliminary_report.md",
                mime="text/markdown",
            )

        with st.expander("Vista previa del reporte en Markdown", expanded=False):
            st.markdown(markdown_text)

    else:
        with download_col1:
            st.warning("No se encontró el reporte Markdown.")

    if REPORT_HTML_PATH.exists():
        html_text = REPORT_HTML_PATH.read_text(encoding="utf-8")

        with download_col2:
            st.download_button(
                label="Descargar reporte HTML (.html)",
                data=html_text.encode("utf-8"),
                file_name="bibliomap_preliminary_report.html",
                mime="text/html",
            )

        with st.expander("Vista previa técnica del HTML generado", expanded=False):
            st.code(html_text[:8000], language="html")

    else:
        with download_col2:
            st.warning("No se encontró el reporte HTML.")

    if REPORT_PDF_PATH.exists():
        pdf_bytes = REPORT_PDF_PATH.read_bytes()

        with download_col3:
            st.download_button(
                label="Descargar reporte PDF (.pdf)",
                data=pdf_bytes,
                file_name="bibliomap_preliminary_report.pdf",
                mime="application/pdf",
            )
    else:
        with download_col3:
            st.warning("No se encontro el reporte PDF. Instala reportlab y genera el reporte.")

    st.info(
        """
        Para entregar al tutor, puedes compartir el archivo HTML como lectura rápida
        y conservar el Markdown como versión editable del informe preliminar.
        """
    )


def page_aprender_bibliometria() -> None:
    """
    Página pedagógica de BiblioMap.
    """
    st.markdown("## Aprender bibliometría")

    st.write(
        """
        Esta sección convierte a BiblioMap en una herramienta formativa.
        Su propósito es ayudar a leer los resultados bibliométricos con criterio
        metodológico, evitando interpretaciones apresuradas.
        """
    )

    st.info(
        """
        Regla de oro: BiblioMap orienta, no sentencia. Una señal bibliométrica
        debe ser revisada, contextualizada y validada por el investigador humano.
        """
    )

    tabs = st.tabs(
        [
            "Conceptos básicos",
            "Cómo leer BiblioMap",
            "Brechas y tendencias",
            "Método recomendado",
            "Glosario mínimo",
            "Cautelas metodológicas",
        ]
    )

    with tabs[0]:
        st.markdown("### Conceptos básicos")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Bibliometría")
            st.write(
                """
                Es el uso de métodos cuantitativos para estudiar publicaciones,
                citas, autores, instituciones, fuentes y patrones de producción científica.
                Permite observar cómo se organiza y circula el conocimiento en un campo.
                """
            )

            st.markdown("#### Bibliometrología")
            st.write(
                """
                En el ecosistema BiblioIntel, la bibliometrología se entiende como
                el saber aplicado que mide, organiza, interpreta y transforma evidencia
                bibliográfica y científica en conocimiento útil para investigar.
                """
            )

            st.markdown("#### Mapeo bibliométrico")
            st.write(
                """
                Es la representación visual o estructurada de relaciones bibliográficas:
                países, autores, instituciones, temas, citas, coautorías, fuentes o redes.
                """
            )

        with col2:
            st.markdown("#### Producción científica")
            st.write(
                """
                Conjunto de publicaciones recuperadas sobre un tema: artículos,
                libros, capítulos, preprints u otros documentos académicos según
                la cobertura de la fuente consultada.
                """
            )

            st.markdown("#### Citas")
            st.write(
                """
                Las citas son referencias recibidas por una publicación. Pueden indicar
                influencia, visibilidad o circulación, pero no necesariamente calidad.
                """
            )

            st.markdown("#### Fuente académica")
            st.write(
                """
                Base o índice desde donde se recuperan metadatos. En este MVP,
                BiblioMap usa OpenAlex como fuente abierta inicial.
                """
            )

    with tabs[1]:
        st.markdown("### Cómo leer BiblioMap")

        st.markdown("#### 1. Buscar tema")
        st.write(
            """
            Es el punto de entrada. Allí se escribe el tema de investigación y las
            palabras clave. La calidad de la búsqueda depende mucho de estos términos.
            """
        )

        st.markdown("#### 2. Resultados preliminares")
        st.write(
            """
            Muestran los registros recuperados. Deben revisarse títulos, años,
            autores, países, instituciones, fuentes, DOI y enlaces. No todo resultado
            recuperado será necesariamente pertinente.
            """
        )

        st.markdown("#### 3. Mapa mundial")
        st.write(
            """
            Permite observar la distribución geográfica de la producción científica.
            Un país más oscuro indica mayor número de publicaciones o citas, según la métrica seleccionada.
            """
        )

        st.warning(
            """
            Una publicación con autores de varios países puede contar para más de un país.
            Por eso el conteo geográfico puede ser mayor que el número total de documentos.
            """
        )

        st.markdown("#### 4. Detalle geográfico")
        st.write(
            """
            Desagrega los datos por país y región. Es útil para identificar polos
            de producción y zonas de baja presencia relativa.
            """
        )

        st.markdown("#### 5. Investigadores y publicaciones")
        st.write(
            """
            Ayudan a ubicar autores, instituciones, fuentes y documentos relevantes.
            Son puntos de partida para lectura, contacto académico y construcción del estado del arte.
            """
        )

    with tabs[2]:
        st.markdown("### Brechas y tendencias")

        st.markdown("#### Brecha preliminar")
        st.write(
            """
            Es una posible zona de investigación poco desarrollada, poco visible,
            poco conectada o insuficientemente abordada dentro de la muestra recuperada.
            """
        )

        st.markdown("#### Tendencia de estudio")
        st.write(
            """
            Es un patrón visible en la muestra: términos frecuentes, crecimiento reciente,
            concentración temporal, polos geográficos o líneas dominantes.
            """
        )

        st.markdown("#### Área poco visible")
        st.write(
            """
            Es una dimensión que aparece poco o no aparece en títulos y abstracts,
            según la búsqueda realizada. No significa que no exista; significa que
            no fue suficientemente detectada en esta muestra.
            """
        )

        st.markdown("#### Oportunidad investigativa")
        st.write(
            """
            Es una formulación preliminar que convierte una señal bibliométrica en
            una posible pregunta, ruta o foco de investigación.
            """
        )

        st.success(
            """
            Fórmula práctica:
            señal bibliométrica + lectura crítica + contexto humano = oportunidad investigativa.
            """
        )

    with tabs[3]:
        st.markdown("### Método recomendado de uso")

        steps = [
            ("Paso 1. Formular el tema", "Escribe el tema de investigación de forma clara. Luego tradúcelo a palabras clave en español e inglés para mejorar cobertura."),
            ("Paso 2. Ejecutar búsqueda exploratoria", "Haz una primera consulta con 50 a 100 resultados. Revisa si los documentos recuperados realmente pertenecen al tema."),
            ("Paso 3. Ajustar términos", "Si hay ruido, elimina palabras ambiguas. Si hay pocos resultados, agrega sinónimos, conceptos cercanos o términos en inglés."),
            ("Paso 4. Leer mapa y detalle geográfico", "Observa qué países, regiones e instituciones aparecen con más fuerza. Luego revisa qué zonas aparecen poco o no aparecen."),
            ("Paso 5. Revisar brechas y tendencias", "Lee las tarjetas de brechas, tendencias, áreas poco visibles y oportunidades. Tómalas como hipótesis iniciales, no como conclusiones cerradas."),
            ("Paso 6. Validar con lectura crítica", "Selecciona documentos clave, lee abstracts, revisa métodos, compara fuentes y construye una matriz manual de hallazgos."),
            ("Paso 7. Contrastar con otras bases", "Cuando el estudio sea formal, contrasta con Scopus, Web of Science, Dimensions, Lens, Google Scholar u otras fuentes pertinentes."),
        ]

        for title, body in steps:
            st.markdown(f"#### {title}")
            st.write(body)

    with tabs[4]:
        st.markdown("### Glosario mínimo")

        glossary = pd.DataFrame(
            [
                {"Término": "Metadatos", "Significado": "Datos descriptivos de una publicación: título, autores, año, DOI, fuente, instituciones, países y citas."},
                {"Término": "Corpus", "Significado": "Conjunto de documentos recuperados para analizar un tema."},
                {"Término": "Coautoría", "Significado": "Relación entre autores que publican juntos."},
                {"Término": "Afiliación", "Significado": "Institución a la que pertenece un autor en una publicación."},
                {"Término": "Citación", "Significado": "Referencia que una publicación recibe de otra."},
                {"Término": "Fuente", "Significado": "Revista, libro, repositorio o plataforma donde aparece una publicación."},
                {"Término": "Tendencia", "Significado": "Patrón visible de crecimiento, concentración o recurrencia temática."},
                {"Término": "Brecha", "Significado": "Zona poco abordada, poco visible o insuficientemente articulada en la literatura recuperada."},
                {"Término": "OpenAlex", "Significado": "Base abierta de metadatos académicos usada por BiblioMap en este MVP."},
                {"Término": "Validación humana", "Significado": "Revisión crítica que debe hacer el investigador antes de aceptar una señal bibliométrica como hallazgo."},
            ]
        )

        st.dataframe(glossary, use_container_width=True, height=420)

    with tabs[5]:
        st.markdown("### Cautelas metodológicas")

        cautions = [
            "Una base de datos no representa toda la ciencia mundial. OpenAlex tiene amplia cobertura, pero no sustituye todas las fuentes académicas.",
            "Más citas no siempre significa más calidad. Las citas pueden reflejar visibilidad, antigüedad, controversia o centralidad, pero no son juicio definitivo de valor.",
            "La ausencia de resultados no prueba ausencia de investigación. Puede deberse a términos de búsqueda, idioma, cobertura, metadatos incompletos o indexación limitada.",
            "Los años recientes suelen estar incompletos. Muchas publicaciones tardan en indexarse o acumular citas.",
            "Las brechas son hipótesis de trabajo. Deben convertirse en preguntas de investigación mediante lectura crítica, delimitación teórica y validación metodológica.",
        ]

        for caution in cautions:
            st.warning(caution)

        st.info(
            """
            Criterio inteligentizador:
            el software procesa evidencia, la IA amplifica interpretación,
            la inteligencia humana profundiza el conocimiento y la creatividad
            transforma los resultados en nuevas rutas investigativas.
            """
        )


def page_placeholder(title: str, description: str) -> None:
    st.markdown(f"## {title}")
    st.write(description)
    st.warning("Esta sección será desarrollada en las próximas fases del MVP.")


def render_footer() -> None:
    st.divider()
    st.markdown(
        """
        <div class="footer-text">
        BiblioMap — Ecosistema BiblioIntel. Desarrollo de LEGIN.
        Mapea la ciencia, encuentra brechas, conecta con el mundo.
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_notificaciones_perfil() -> None:
    st.markdown("## Perfiles de Usuario y Notificaciones Multicanal")
    st.write(
        """
        Gestiona los perfiles de los investigadores, sus temas de interés académico
        y configura los canales (Gmail, Telegram, WhatsApp) para recibir alertas 
        automáticas cuando se encuentren publicaciones coincidentes.
        """
    )

    # User selection
    usuarios = get_users()
    options = {f"{u['nombre']} ({u['email']})": u['id'] for u in usuarios}
    
    col_sel, col_new = st.columns([3, 1])
    with col_sel:
        selected_user_label = st.selectbox(
            "Seleccionar Investigador", 
            options=list(options.keys()) + ["-- Crear Nuevo Perfil --"]
        )
    
    user_id = None
    is_new_user = selected_user_label == "-- Crear Nuevo Perfil --"
    
    if not is_new_user:
        user_id = options[selected_user_label]
        user_data = get_user_by_id(user_id)
    else:
        user_data = {"nombre": "", "email": "", "telefono": ""}

    st.markdown("### 👤 Datos Personales")
    with st.form("user_profile_form"):
        nombre = st.text_input("Nombre Completo", value=user_data["nombre"])
        email = st.text_input("Correo Electrónico", value=user_data["email"])
        telefono = st.text_input("Teléfono Celular (WhatsApp)", value=user_data["telefono"], help="Ejemplo: +584121234567")
        
        save_profile = st.form_submit_button("Guardar Perfil")
        
        if save_profile:
            if not nombre or not email:
                st.error("El nombre y correo electrónico son obligatorios.")
            else:
                if is_new_user:
                    create_user(nombre, email, telefono)
                    st.success("Perfil creado exitosamente.")
                    st.rerun()
                else:
                    update_user(user_id, nombre, email, telefono)
                    st.success("Perfil actualizado exitosamente.")
                    st.rerun()

    if user_id:
        st.divider()
        col_interests, col_channels = st.columns(2)

        with col_interests:
            st.markdown("### 📚 Temas de Interés")
            intereses = get_user_interests(user_id)
            
            if intereses:
                st.write("Palabras clave registradas:")
                for i, interes in enumerate(intereses):
                    c_text, c_btn = st.columns([4, 1])
                    c_text.markdown(f"- **{interes}**")
                    if c_btn.button("🗑️", key=f"del_int_{i}_{interes}"):
                        remove_user_interest(user_id, interes)
                        st.success(f"Interés '{interes}' eliminado.")
                        st.rerun()
            else:
                st.info("No tienes temas de interés registrados todavía.")

            st.write("---")
            with st.form("add_interest_form"):
                nuevo_interes = st.text_input("Agregar nueva palabra clave de interés")
                add_btn = st.form_submit_button("Agregar Interés")
                if add_btn and nuevo_interes.strip():
                    added = add_user_interest(user_id, nuevo_interes)
                    if added:
                        st.success(f"Interés '{nuevo_interes}' agregado.")
                        st.rerun()
                    else:
                        st.warning("Ese interés ya está registrado o está vacío.")

        with col_channels:
            st.markdown("### 🔔 Configuración de Canales")
            prefs = get_user_preferences(user_id)
            
            # SMTP
            smtp_active = st.checkbox("Correo Electrónico (Gmail SMTP)", value=prefs.get("SMTP", {}).get("activo", False))
            
            # Telegram
            tg_active = st.checkbox("Telegram (Bot API)", value=prefs.get("TELEGRAM", {}).get("activo", False))
            tg_chat_id = st.text_input(
                "ID de Chat de Telegram", 
                value=prefs.get("TELEGRAM", {}).get("config", {}).get("chat_id", ""),
                help="Puedes obtener tu ID iniciando chat con @userinfobot en Telegram."
            )
            
            # WhatsApp
            wa_active = st.checkbox("WhatsApp (API WAHA)", value=prefs.get("WHATSAPP", {}).get("activo", False))
            
            save_prefs = st.button("Guardar Preferencias de Canal")
            if save_prefs:
                update_user_preference(user_id, "SMTP", smtp_active, {})
                update_user_preference(user_id, "TELEGRAM", tg_active, {"chat_id": tg_chat_id})
                update_user_preference(user_id, "WHATSAPP", wa_active, {})
                st.success("Preferencias guardadas exitosamente.")
                st.rerun()

            st.write("---")
            st.markdown("#### 🧪 Pruebas de Notificación")
            if st.button("Enviar Alerta de Prueba"):
                with st.spinner("Enviando alertas de prueba..."):
                    res = send_notification_multichannel(
                        user_id=user_id,
                        title="[PRUEBA] Alerta de Inteligencia Artificial en BiblioMap",
                        link="https://openalex.org/W12345678",
                        summary="Esta es una notificación de prueba para validar tus canales de comunicación activos."
                    )
                st.write("Resultados del envío:")
                for canal, status in res.items():
                    if status == "EXITOSO":
                        st.success(f"{canal}: {status}")
                    elif "ENCOLADO" in status:
                        st.info(f"{canal}: {status}")
                    else:
                        st.error(f"{canal}: {status}")

        st.divider()
        st.markdown("### 📥 Cola y Control Anti-Baneo de WhatsApp")
        col_queue_status, col_queue_action = st.columns([3, 1])
        
        from modules.database import get_pending_notifications
        pending = get_pending_notifications()
        
        with col_queue_status:
            if pending:
                st.warning(f"Hay {len(pending)} alertas pendientes de envío en la cola de WhatsApp.")
                queue_data = [{"ID": p["id"], "Usuario ID": p["usuario_id"], "Artículo": p["titulo_articulo"], "Creado en": p["creado_en"]} for p in pending]
                st.dataframe(pd.DataFrame(queue_data))
            else:
                st.success("La cola de WhatsApp está vacía. Todos los mensajes han sido enviados.")
                
        with col_queue_action:
            if st.button("Procesar Cola de WhatsApp"):
                with st.spinner("Procesando cola..."):
                    sent = process_whatsapp_queue()
                if sent > 0:
                    st.success(f"Se enviaron {sent} mensajes de WhatsApp pendientes.")
                else:
                    st.info("No se enviaron mensajes (aún bajo el límite de tiempo de 1 minuto o cola vacía).")
                st.rerun()

        st.divider()
        st.markdown("### 📜 Historial de Alertas Enviadas")
        history = get_notification_history(user_id)
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(df_hist[["enviado_en", "canal", "titulo_articulo", "estado"]])
        else:
            st.info("No hay historial de envíos registrado para este usuario.")


def start_queue_worker() -> None:
    """Starts a background thread to process the WhatsApp queue automatically."""
    import threading
    # Check if worker thread is already running to avoid duplicates
    for t in threading.enumerate():
        if t.name == "BiblioMapQueueWorker":
            return
            
    def run_worker():
        import time
        from modules.notifier import process_whatsapp_queue
        while True:
            try:
                process_whatsapp_queue()
            except Exception:
                pass
            time.sleep(15) # Check queue every 15 seconds
            
    thread = threading.Thread(target=run_worker, name="BiblioMapQueueWorker", daemon=True)
    thread.start()


def main() -> None:
    st.set_page_config(
        page_title="BiblioMap",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize the notification database
    initialize_db()

    # Start background queue worker for WhatsApp
    start_queue_worker()

    init_session_state()
    load_css()
    render_top_navigation()
    render_sidebar()
    menu = st.session_state.current_page

    if menu == "Inicio":
        page_inicio()

    elif menu == "Buscar tema":
        page_buscar_tema()

    elif menu == "Mapa mundial":
        page_mapa_mundial()

    elif menu == "Detalle geográfico":
        page_detalle_geografico()

    elif menu == "Investigadores":
        page_investigadores()

    elif menu == "Publicaciones":
        page_publicaciones()

    elif menu == "Brechas preliminares":
        page_brechas_preliminares()

    elif menu == "Reporte preliminar":
        page_reporte_preliminar()

    elif menu == "Usuarios y Notificaciones":
        page_notificaciones_perfil()

    elif menu == "Aprender bibliometría":
        page_aprender_bibliometria()

    render_footer()


if __name__ == "__main__":
    main()
