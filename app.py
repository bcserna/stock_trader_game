import streamlit as st
from game import Game
from plotly_display import candlestick, CANDLESTICK_CONFIG, pie_chart, PIE_CONFIG

st.set_page_config(
    page_title='📈🚀',
    page_icon='😎',
    initial_sidebar_state='expanded',
    layout='wide'
)

STATE = st.session_state
if 'body' not in STATE:
    STATE.body = st.empty()


def on_start_click():
    with st.spinner('Loading...'):
        print('Player name:', STATE.player)
        STATE.game = Game(['Microsoft', 'Apple'])
        STATE.game_initialized = True
        STATE.stock_price_plot_invalid = True
        STATE.portfolio_plot_invalid = True


def display_start_menu():
    with STATE.body.container():
        st.write('Game setup')
        STATE.player = st.text_input('Player name')
        # stock_selector = st.multiselect('Stocks to include', TICKERS.keys())
        # period = st.selectbox(label='Simulation period (years)', options=[3, 5])
        st.button('Start', type='primary', on_click=on_start_click)


def update_portfolio_data():
    STATE.funds = STATE.game.funds[STATE.player]

    stock_value = STATE.game.get_stock_value(STATE.player)
    total_value = STATE.game.get_total_value(STATE.player)

    if 'stock_value' in STATE:
        STATE.stock_delta = stock_value - STATE.stock_value
        STATE.value_delta = total_value - STATE.total_value
    else:
        STATE.stock_delta = 0
        STATE.value_delta = 0

    STATE.stock_value = stock_value
    STATE.total_value = total_value


def display_sidebar():
    with st.sidebar.container():
        # Player data
        col1, col2 = st.columns(2)
        with col1:
            st.caption(STATE.player)
            st.metric('Funds', f'{STATE.funds}')
        with col2:
            st.caption(f'_Day {STATE.game.day_progress[STATE.player]}_')
            st.metric('Portfolio value', f'{round(STATE.total_value, 1)}', int(round(STATE.value_delta, 0)))

        # Day progress control
        st.divider()
        days = st.number_input('Progress days', 1, 30)
        st.button('Go', type='primary', on_click=on_progress_click, args=(days,))

        # Order control
        st.divider()
        selected_stock = st.selectbox('Stock', list(STATE.game.stock_data.keys()))
        current_price = STATE.game.stock_price(selected_stock, STATE.game.day_progress[STATE.player])
        st.caption(f'Current price: `{current_price:.1f}`')
        selected_order = st.select_slider('Order', ['BUY', 'SELL'], label_visibility='collapsed')
        max_order = STATE.game.max_order(STATE.player, selected_stock, selected_order)
        amount = st.number_input('Amount', 0, max_order)
        value = current_price * amount
        st.caption(f'Order value: `{round(value)}`')
        st.button('Confirm order', type='primary', on_click=on_order_click,
                  args=(selected_order, STATE.player, selected_stock, amount))


def on_progress_click(days):
    if days > 0:
        STATE.game.progress_days(STATE.player, days)
        STATE.stock_price_plot_invalid = True
        STATE.portfolio_plot_invalid = True


def on_order_click(order, player, stock, amount):
    if amount > 0:
        if order.lower() == 'buy':
            STATE.game.buy(player, stock, amount)
        elif order.lower() == 'sell':
            STATE.game.sell(player, stock, amount)
        print(player, order, stock, amount)
        STATE.portfolio_plot_invalid = True


def generate_stock_price_plots():
    stock_data = STATE.game.get_available_stock_data(STATE.player)
    STATE.stock_price_plots = {name: candlestick(df) for name, df in stock_data.items()}
    STATE.stock_price_plot_invalid = False


def generate_portfolio_plots():
    g = STATE.game
    p = STATE.player
    stock_amounts = g.stock_amount[p]

    data = dict(Funds=STATE.game.funds[STATE.player])
    for stock in g.stock_data.keys():
        data[stock] = g.stock_price(stock, g.day_progress[p]) * stock_amounts[stock]
    STATE.portfolio_pie = pie_chart(data)
    STATE.portfolio_plot_invalid = False


def display_stocks():
    with st.container():
        st.header('Stock price')

        if STATE.stock_price_plot_invalid:
            generate_stock_price_plots()

        for name, fig in STATE.stock_price_plots.items():
            expander = st.expander(name, expanded=True)
            expander.plotly_chart(fig, use_container_width=True, config=CANDLESTICK_CONFIG)


def display_portfolio():
    col1, col2 = st.columns(2)

    # Portfolio metrics
    with col1:
        st.caption(':sunglasses:')
        st.metric('Funds', STATE.funds)
        st.metric('Stock value', f'{STATE.stock_value:.1f}', delta=round(STATE.stock_delta, 1))
        st.metric('Total value', f'{STATE.total_value:.1f}', delta=round(STATE.value_delta, 1))

    # Portfolio pie chart
    if STATE.portfolio_plot_invalid:
        generate_portfolio_plots()

    with col2:
        st.plotly_chart(STATE.portfolio_pie, use_container_width=True, config=PIE_CONFIG)


def display_game():
    display_sidebar()

    with STATE.body.container():
        tab1, tab2 = st.tabs(['Stock price', 'Portfolio'])
        with tab1:
            display_stocks()
        with tab2:
            display_portfolio()


if 'game_initialized' not in st.session_state:
    display_start_menu()

if 'game_initialized' in STATE:
    update_portfolio_data()
    display_game()
