
import plotly.graph_objects as go


def _show_price_comparision_graph(data_df, rebase=False):

    min_date = data_df.index.min().date()
    max_date = data_df.index.max().date()

    layout_msg = f"Stocks Price comparision from {min_date} to {max_date}. ".title()
    if rebase:
        data_df = data_df.rebase()
        layout_msg = f"Stocks Price comparision from {min_date} to {max_date} with Price Rebased to 100.".title()
    traces = []
    for stock in list(data_df.columns):
        trace = go.Scatter(
            x=data_df.index,
            y=data_df[stock],
            mode="lines",
            name=stock.upper(),
        )
        traces.append(trace)
    layout = go.Layout(
        title=layout_msg,
        autosize=True,
        width=1100,
        height=600,
        # margin=go.layout.Margin(l=50, r=10, b=50, t=50, pad=4),
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(
        # Shows gray line without grid, styling fonts, linewidths and more
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=2,
            ticks="outside",
            tickfont=dict(
                family="Arial",
                size=12,
                color="rgb(82, 82, 82)",
            ),
        ),
        # Turn off everything on y axis
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True,
        plot_bgcolor="white",
    )
    return fig
