import plotly.graph_objects as go

CANDLESTICK_CONFIG = dict(
    scrollZoom=True,
    displayModeBar=True,
    displaylogo=False,
    modeBarButtonsToRemove=('toImage', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'lasso2d')
)

PIE_CONFIG = dict(
    displayModeBar=False
)


def candlestick(df):
    df = df.copy()
    candlestick = go.Candlestick(
        x=df.date,
        open=df.rel_open,
        close=df.rel_close,
        high=df.rel_high,
        low=df.rel_low,
    )

    fig = go.Figure(data=[candlestick])
    margin = dict(l=10, r=10, t=15, b=10)
    xaxis = dict(
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5D", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(label='All', step="all")
            ])
        ),
        rangeslider=dict(visible=False),
        type='date',
    )

    fig.update_layout(
        height=280,
        margin=margin,
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        xaxis=xaxis
    )

    return fig


def pie_chart(data):
    pull = [0] * len(data)
    pull[list(data).index('Funds')] = 0.1

    pie = go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        textinfo='label+percent',
        insidetextorientation='radial',
        pull=pull,
        sort=False,
        hoverinfo='skip',
    )
    fig = go.Figure(data=[pie])

    margin = dict(l=10, r=10, t=40, b=10)

    fig.update_layout(showlegend=False, margin=margin)
    return fig
