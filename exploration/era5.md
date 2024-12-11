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

# ERA5

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import calendar

import matplotlib.pyplot as plt

from src.datasources import codab, era5
from src.constants import *
```

```python
# codab.download_codab_to_blob()
```

```python
adm1 = codab.load_codab_from_blob(admin_level=1)
```

```python
adm1.plot()
```

```python
era5_df = era5.load_era5()
era5_df = era5_df.merge(adm1[[x for x in adm1.columns if "ADM" in x]])
```

```python
era5_df["valid_date"].max()
```

```python
era5_df.dtypes
```

```python
for pcode in AOI_ADM1_PCODES:
    dff = era5_df[era5_df["ADM1_PCODE"] == pcode]

    fig, ax = plt.subplots(dpi=200)
    dff.groupby(dff["valid_date"].dt.month.rename("month"))[
        "mean"
    ].mean().reset_index().plot.bar(x="month", y="mean", ax=ax)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend().remove()
    ax.set_ylabel("Précipitations journalières moyennes (mm)")
    ax.set_xlabel("Mois")
    ax.set_title(dff.iloc[0]["ADM1_FR"])
```

```python
valid_month = 10
min_year = 2000

right_edge = 2024 + 0.99
upper_color = "dodgerblue"
middle_color = "grey"
lower_color = "goldenrod"
alpha = 0.1

for pcode in AOI_ADM1_PCODES:
    dff = era5_df[
        (era5_df["ADM1_PCODE"] == pcode)
        & (era5_df["valid_date"].dt.month == valid_month)
        & (era5_df["valid_date"].dt.year >= min_year)
    ].copy()
    dff["year"] = dff["valid_date"].dt.year
    upper_tercile = dff["mean"].quantile(2 / 3)
    lower_tercile = dff["mean"].quantile(1 / 3)
    current_value = dff.set_index("year").loc[2024, "mean"]
    top_edge = dff["mean"].max() * 1.1

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
    ax.set_ylim(bottom=0, top=top_edge)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        f'{dff.iloc[0]["ADM1_FR"]} - '
        f"{FRENCH_MONTHS.get(calendar.month_abbr[valid_month])}"
    )
```

```python

```
