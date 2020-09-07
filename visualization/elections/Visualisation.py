# %%
import pandas as pd

import plotly.offline as offline
import plotly.graph_objs as go

from typing import Dict, Tuple
from pandas import DataFrame


# %%


def dfs_from_year(year: int) -> Tuple[DataFrame, DataFrame]:
    parties = pd.read_csv(
        f"~/data/parties_{year}.csv",
        low_memory=False,
        index_col=["region", "town", "district_no"],
    )
    districts = pd.read_csv(
        f"~/data/districts_{year}.csv",
        low_memory=False,
        index_col=["region", "town", "district_no"],
    )
    return parties, districts


mandates = pd.read_csv("~/data/mandaty.csv", index_col=["year", "region"])

# %%
mandates.head(3)


# %%


def who_would_win(year: int) -> Dict[str, int]:
    parties, districts = dfs_from_year(year)

    result: Dict[str, int] = {}
    for _, group in parties.groupby(["region", "town", "district_no"]):
        sorted = group.sort_values("n_votes", ascending=False)
        top_row = sorted.iloc[0]
        party_name = top_row["party_name"]
        val = result.setdefault(party_name, 0)
        result[party_name] = val + 1
    return result


# %%


def plot(dic: Dict[str, int], year: int) -> None:
    mds = mandates.groupby(["year"]).get_group(year)
    dic2 = {}
    for party in dic.keys():
        dic2[party] = mds[party].sum() if party in mds else 0

    results = sorted([(k, v) for k, v in dic.items()], key=lambda tu: tu[1])
    trace1 = go.Bar(name="okrsků", x=[k for k, _ in results], y=[v for _, v in results])

    trace2 = go.Scatter(
        name="mandátů",
        x=[k for k, _ in results],
        y=[dic2[k] for k, _ in results],
        yaxis="y2",
    )

    data = [trace1, trace2]

    fig = dict(
        data=data,
        layout=dict(
            title=f"Seřazení stran podle výsledku v jedntolivých okrscích v roce {year}",
            yaxis=dict(title="Počet vyhraných okrsků"),
            yaxis2=dict(
                title="Počet získaných mandátů",
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, 90],
            ),
        ),
    )

    offline.plot(fig)


# %%
parties_2006 = who_would_win(2006)


# %%
plot(parties_2006, year=2006)
