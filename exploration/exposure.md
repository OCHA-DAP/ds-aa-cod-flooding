---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-aa-cod-flooding
    language: python
    name: ds-aa-cod-flooding
---

# Flood exposure

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sqlalchemy import text

from src.datasources import codab
from src.utils import db_utils
from src.constants import *
```

```python
adm1 = codab.load_codab_from_blob(admin_level=1)
```

```python
adm1.plot()
```

```python
query = f"""
SELECT *
FROM app.floodscan_exposure
WHERE iso3='{ISO3.upper()}' AND adm_level=1
"""
```

```python
exposure_df = pd.read_sql(query, db_utils.get_engine(stage="dev"))
```

```python
exposure_df = exposure_df.rename(columns={"pcode": "ADM1_PCODE"})
```

```python
exposure_df = exposure_df.merge(adm1[[x for x in adm1.columns if "ADM" in x]])
```

```python
exposure_df["valid_date"] = pd.to_datetime(exposure_df["valid_date"])
```

```python
def add_floodseason(x):
    x = x.date()
    return x.year - 1 if x.month < 9 else x.year
```

```python
exposure_df["floodseason"] = exposure_df["valid_date"].apply(add_floodseason)
```

```python
exposure_df["floodseason_str"] = exposure_df["floodseason"].apply(
    lambda x: f"{x}/{x+1}"
)
```

```python
exposure_df = exposure_df.sort_values(["ADM1_PCODE", "valid_date"])
```

```python
exposure_df["roll7"] = (
    exposure_df.groupby("ADM1_PCODE")["sum"]
    .rolling(7)
    .mean()
    .reset_index(level=0, drop=True)
)
```

```python
exposure_df
```

```python
yearly_max_df = (
    exposure_df.groupby(["ADM1_PCODE", "floodseason", "floodseason_str"])[
        "roll7"
    ]
    .max()
    .reset_index()
)
```

```python
yearly_max_df = yearly_max_df.merge(adm1[["ADM1_PCODE", "ADM1_FR"]])
```

```python
def plot_exposure(dff):
    q2_color = "darkorange"
    q3_color = "crimson"
    q4_color = "rebeccapurple"
    alpha = 0.1
    linewidth = 1
    fig, ax = plt.subplots(dpi=200)
    colors = ["k"] * (len(dff) - 1) + ["white"]
    dff.plot.bar(
        ax=ax,
        x="floodseason_str",
        y="roll7",
        color=colors,
        edgecolor=["k"] * len(dff),  # Ensure the last bar has a black edge
        hatch=[""] * (len(dff) - 1)
        + ["////"],  # Apply hatch only to the last bar
        rot=90,  # Rotate x-axis labels
        zorder=3,
    )

    quartile_1 = dff["roll7"].quantile(1 / 4)
    quartile_2 = dff["roll7"].quantile(2 / 4)
    quartile_3 = dff["roll7"].quantile(3 / 4)

    current_value = dff.set_index("floodseason").loc[2024, "roll7"]

    top_edge = dff["roll7"].max() * 1.05

    ax.axhline(y=quartile_1, color=q2_color, linewidth=linewidth)
    ax.axhspan(
        ymin=quartile_1,
        ymax=quartile_2,
        facecolor=q2_color,
        alpha=alpha,
    )
    ax.text(
        ax.get_xlim()[1],  # Position off the right edge of the plot
        quartile_1,  # Y-coordinate (height of the bar)
        f" 25e qtl. : {int(quartile_1):,} pers.".replace(
            ",", " "
        ),  # Format the text
        ha="left",
        fontsize=8,  # Text alignment and size
        color=q2_color,
    )
    ax.axhline(y=quartile_2, color=q3_color, linewidth=linewidth)
    ax.axhspan(
        ymin=quartile_2,
        ymax=quartile_3,
        facecolor=q3_color,
        alpha=alpha,
    )
    ax.text(
        ax.get_xlim()[1],  # Position off the right edge of the plot
        quartile_2,  # Y-coordinate (height of the bar)
        f" 50e qtl. : {int(quartile_2):,} pers.".replace(
            ",", " "
        ),  # Format the text
        ha="left",
        fontsize=8,  # Text alignment and size
        color=q3_color,
    )
    ax.axhline(y=quartile_3, color=q4_color, linewidth=linewidth)
    ax.axhspan(
        ymin=quartile_3,
        ymax=top_edge,
        facecolor=q4_color,
        alpha=alpha,
    )
    ax.text(
        ax.get_xlim()[1],  # Position off the right edge of the plot
        quartile_3,  # Y-coordinate (height of the bar)
        f" 75e qtl. : {int(quartile_3):,} pers.".replace(
            ",", " "
        ),  # Format the text
        ha="left",
        fontsize=8,  # Text alignment and size
        color=q4_color,
    )

    ax.set_title(dff.iloc[0]["ADM1_FR"])
    ax.set_ylabel("Population exposée aux inondations")
    ax.set_xlabel("Saison d'inondations (commence début sept.)")

    ax.set_ylim(bottom=0, top=top_edge)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, pos: f"{int(x):,}".replace(",", " "))
    )
    ax.legend().remove()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
```

```python
for pcode in AOI_ADM1_PCODES:
    dff = yearly_max_df[yearly_max_df["ADM1_PCODE"] == pcode]
    plot_exposure(dff)
```

```python
dff_aoi = (
    yearly_max_df[yearly_max_df["ADM1_PCODE"].isin(AOI_ADM1_PCODES)]
    .groupby(["floodseason", "floodseason_str"])["roll7"]
    .sum()
    .reset_index()
)
dff_aoi["ADM1_FR"] = "Toutes provinces"
```

```python
plot_exposure(dff_aoi)
```

```python
for zone in ZONES:
    dff_zone = yearly_max_df[
        yearly_max_df["ADM1_PCODE"].isin(zone.get("pcodes"))
    ].copy()
    dff_zone_grouped = (
        dff_zone.groupby(["floodseason", "floodseason_str"])["roll7"]
        .sum()
        .reset_index()
    )
    names = dff_zone["ADM1_FR"].unique()
    dff_zone_grouped["ADM1_FR"] = (
        f'Zone {zone.get("number")} ({", ".join(names)})'
    )
    plot_exposure(dff_zone_grouped)
```

```python
dff_zone_grouped["ADM1_FR"]
```

```python
plot_exposure(yearly_max_df[yearly_max_df["ADM1_PCODE"] == KINSHASA1])
```

```python
plot_exposure(yearly_max_df[yearly_max_df["ADM1_PCODE"] == EQUATEUR1])
```
