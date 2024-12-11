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

# SEAS5

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import calendar

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from src.datasources import seas5, codab
from src.constants import *
```

```python
adm1 = codab.load_codab_from_blob(admin_level=1)
```

```python
issued_month = 12
```

```python
seas5_df = seas5.load_seas5(
    valid_months=[12, 1], issue_months=[issued_month], iso3=ISO3
)
seas5_df = seas5_df.merge(adm1[[x for x in adm1.columns if "ADM" in x]])
```

```python
seas5_df
```

```python
def get_french_month_abbr(month_num):
    return FRENCH_MONTHS.get(calendar.month_abbr[month_num])
```

```python
valid_months = [12, 1]
min_year = 2000

right_edge = 2024 + 0.99
upper_color = "dodgerblue"
middle_color = "grey"
lower_color = "goldenrod"
alpha = 0.1
buffer = 0.2

for pcode in AOI_ADM1_PCODES:
    dff = seas5_df[
        (seas5_df["ADM1_PCODE"] == pcode)
        & (seas5_df["valid_date"].dt.month.isin(valid_months))
        & (seas5_df["issued_date"].dt.year >= min_year)
    ].copy()
    adm_name = dff.iloc[0]["ADM1_FR"]

    dff = dff.groupby("issued_date")["mean"].mean().reset_index()
    dff["year"] = dff["issued_date"].dt.year

    upper_tercile = dff["mean"].quantile(2 / 3)
    lower_tercile = dff["mean"].quantile(1 / 3)
    current_value = dff.set_index("year").loc[2024, "mean"]
    values_range = dff["mean"].max() - dff["mean"].min()
    top_edge = dff["mean"].max() + values_range * buffer
    bottom_edge = max(dff["mean"].min() - values_range * buffer, 0)

    fig, ax = plt.subplots(dpi=200)
    dff.plot(x="year", y="mean", ax=ax, color="k")

    for year, row in dff.set_index("year").iterrows():
        if row["mean"] > upper_tercile:
            ax.annotate(
                year,
                (year, row["mean"]),
                fontsize=8,
                ha="center",
                color="grey",
                xytext=(0, 2),
                textcoords="offset points",
            )

    ax.annotate(
        2024,
        (2024, current_value),
        ha="center",
        xytext=(0, 5),
        textcoords="offset points",
    )
    ax.plot([2024], [current_value], marker=".", color="k")

    ax.plot([right_edge, right_edge], [0, lower_tercile], color=lower_color)
    ax.axhspan(
        ymin=0,
        ymax=lower_tercile,
        facecolor=lower_color,
        alpha=alpha,
    )
    ax.plot(
        [right_edge, right_edge],
        [lower_tercile, upper_tercile],
        color=middle_color,
    )
    ax.axhspan(
        ymin=upper_tercile,
        ymax=dff["mean"].max() * 2,
        facecolor=upper_color,
        alpha=alpha,
    )
    ax.plot(
        [right_edge, right_edge],
        [upper_tercile, dff["mean"].max() * 2],
        color=upper_color,
    )
    ax.annotate(
        " Terciles:", (right_edge, top_edge), color="k", fontstyle="italic"
    )
    ax.annotate(
        " supérieur\n à normale\n",
        (right_edge, upper_tercile),
        color=upper_color,
    )
    ax.annotate(
        " normale",
        (right_edge, (upper_tercile + lower_tercile) / 2),
        color=middle_color,
        va="center",
    )
    ax.annotate(
        "\n inférieur\n à normale",
        (right_edge, lower_tercile),
        color=lower_color,
        va="top",
    )

    ax.legend().remove()
    ax.set_ylabel(f"Précipitations journalières moyennes (mm)")
    ax.set_xlabel("Année")
    ax.set_xlim(left=min_year, right=right_edge)
    ax.set_ylim(top=top_edge, bottom=bottom_edge)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        f"{adm_name}\nprévisions émises "
        f"{get_french_month_abbr(issued_month)} pour "
        f'{", ".join([get_french_month_abbr(x) for x in valid_months])}'
    )
```

```python
def calculate_rp(group, col_name):
    group[f"rank_{col_name}"] = group[col_name].rank(ascending=False)
    group[f"rp_{col_name}"] = (len(group) + 1) / group[f"rank_{col_name}"]
    return group
```

```python
seas5_df
```

```python
col_name = "mean"
seas5_grouped = (
    seas5_df[seas5_df["issued_date"].dt.year >= min_year]
    .groupby(["ADM1_PCODE", "ADM1_FR", "issued_date"])[col_name]
    .mean()
    .reset_index()
)
seas5_grouped = (
    seas5_grouped.groupby(["ADM1_PCODE", "ADM1_FR"])
    .apply(calculate_rp, col_name=col_name, include_groups=False)
    .reset_index()
    .drop(columns="level_2")
)
```

```python
seas5_grouped
```

```python
seas5_2024 = seas5_grouped[seas5_grouped["issued_date"].dt.year == 2024]
```

```python
!python --version
```

```python
!pip list
```

```python
bounds = [1, 2, 3, 5, 10, 20]
colors = [
    "whitesmoke",
    "lemonchiffon",
    "gold",
    "darkorange",
    "crimson",
    "rebeccapurple",
]

cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bounds, cmap.N, extend="max")
```

```python
gdf_plot = adm1.merge(seas5_2024)
```

```python
fig, ax = plt.subplots(dpi=200, figsize=(8, 8))
gdf_plot.plot(
    column="rp_mean",
    ax=ax,
    cmap=cmap,
    norm=norm,
    legend=True,
    legend_kwds={
        "label": "Période de retour (ans)",
        "shrink": 0.6,
    },
)
gdf_plot.boundary.plot(ax=ax, color="k", linewidth=0.3)
ax.axis("off")
ax.set_title(
    f"Période de retour de précipitations élevées par province,\n prévisions émises "
    f"{get_french_month_abbr(issued_month)} pour "
    f'{", ".join([get_french_month_abbr(x) for x in valid_months])}'
)
for adm_name, row in gdf_plot.set_index("ADM1_FR").iterrows():
    if row["rp_mean"] >= 2:
        ax.annotate(
            adm_name,
            (row.geometry.centroid.x, row.geometry.centroid.y),
            va="center",
            ha="center",
            fontsize=8,
        )
```

```python
row.geometry.centroid.x
```

```python

```
