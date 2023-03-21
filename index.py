from dash import Dash,Input,Output,dcc,html
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import dash.exceptions

# get the data frame from csv file

retail = pd.read_csv('sales-data.csv')
retail['Date'] = pd.to_datetime(retail['Date'], format='%Y-%m-%d')

# monthly sales

monthly_sales_df = retail.groupby(['month']).agg({'Weekly_Sales': 'sum'}).reset_index()
monthly_sales = retail.groupby(['month','Month']).agg({'Weekly_Sales': 'sum'}).reset_index()

# mean weekly sale for months

monthly_sales_dates = retail.groupby(['month','Month','Date']).agg({'Weekly_Sales': 'sum'}).reset_index()
monthly_sales_dates_mean = monthly_sales_dates.groupby(['month','Month']).agg({'Weekly_Sales': 'mean'}).reset_index()
monthly_sales_dates_mean.rename(columns = {'Weekly_Sales':'mean_weekly_sale_for_month'},inplace=True)


# holiday sales
holiday_sales = retail[retail['IsHoliday'] == 1].groupby(['month','Month'])['Weekly_Sales'].sum().reset_index().rename(
    columns={'Weekly_Sales': 'Holiday_Sales'})

# merged above data frames
monthly_sales_df = pd.merge(holiday_sales, monthly_sales_df, on='month', how='right').fillna(0)
monthly_sales_df['Weekly_Sales'] = monthly_sales_df['Weekly_Sales'].round(1)
monthly_sales_df['Holiday_Sales'] = monthly_sales_df['Holiday_Sales'].round(1)

# weekly sales -> graph 1
weekly_sale = retail.groupby(['month', 'Month', 'Date']).agg({'Weekly_Sales': 'sum'}).reset_index()
weekly_sale['week_no'] = weekly_sale.groupby(['Month'])['Date'].rank(method='min')

# sales - storewise

store_df = retail.groupby(['month', 'Month', 'Store']).agg({'Weekly_Sales': 'sum'}).reset_index()
store_df['Store'] = store_df['Store'].apply(lambda x: 'Store' + " " + str(x))
store_df['Weekly_Sales'] = store_df['Weekly_Sales'].round(1)

# sales - department wise
dept_df = retail.groupby(['month', 'Month', 'Dept']).agg({'Weekly_Sales': 'sum'}).reset_index()
dept_df['Dept'] = dept_df['Dept'].apply(lambda x: 'Dept' + " " + str(x))
dept_df['Weekly_Sales'] = dept_df['Weekly_Sales'].round(1)

# create an instance of Dash and specify server for gunicorn
app = Dash(__name__,meta_tags=[{'name':'viewport', 'content':'width=device-width'}])
server = app.server


# browser tab styling
app.title='Sales Comparison Dashboard'


# find list of unique months for dropdown

month_unique = list(retail['Month'].unique())

# define the graphs

fig1=dcc.Graph(id = 'week_line_chart1', config = {'displayModeBar':False},figure = {})

fig2=dbc.Row([
    dbc.Col([dcc.Graph(id = 'store_bar_graph1', config = {'displayModeBar':False})]),
    dbc.Col([dcc.Graph(id = 'store_bar_graph2',config = {'displayModeBar':False})]),
])
fig3=dbc.Row([
    dbc.Col([dcc.Graph(id = 'dept_funnel_graph1', config = {'displayModeBar':False})]),
    dbc.Col([dcc.Graph(id = 'dept_funnel_graph2', config = {'displayModeBar':False})]),
])

fig4 = dcc.Graph(id = 'holiday_bar_graph1',config = {'displayModeBar':False})

fig5 = dcc.Graph(id = 'month_complete_year',config = {'displayModeBar':False})

none_graph = px.scatter(x = [0],y=[0],
                        labels={'x':'','y':''},
                        title = 'Choose a month from title dropdown menu to display graph'.title(),
                        template='plotly_dark'
                        )

# define the cards for numerical data

card_row1_1 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Total Sales',className='title_card'),
            html.H5(id = 'first_sales',className = 'value_card'),
            html.Sub(id = 'first_month_1',className='month_card')
        ]
    )

,className='card_class')

card_row1_2 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Holiday Sales',className='title_card'),
            html.H5(id = 'first_holiday_sales',className = 'value_card'),
            html.Sub(id = 'first_month_2',className='month_card')
        ]
    )

,className='card_class')

card_row1_3 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Departments',className='title_card'),
            html.H5(id = 'first_stores',className = 'value_card'),
            html.Sub(id = 'first_month_3',className='month_card')
        ]
    )

,className='card_class')



card_change1 = dbc.Card(

    dbc.CardBody([

        html.P('Change',className='value_card'),
        html.H5(id = 'sales_change',className='value_card')
    ])
,className='card_class')

card_change2 = dbc.Card(

    dbc.CardBody([

        html.P('Change',className='value_card'),
        html.H5(id = 'holiday_sales_change',className='value_card')
    ])
,className='card_class')

card_change3 = dbc.Card(

    dbc.CardBody([

        html.P('Change',className='value_card'),
        html.H5(id = 'store_change',className='value_card')
    ])
,className='card_class')


card_row3_1 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Total Sales',className='title_card'),
            html.H5(id = 'second_sales',className = 'value_card'),
            html.Sub(id = 'second_month_1',className='month_card')
        ]
    )

,className='card_class')

card_row3_2 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Holiday Sales',className='title_card'),
            html.H5(id = 'second_holiday_sale',className = 'value_card'),
            html.Sub(id = 'second_month_2',className='month_card')
        ]
    )

,className='card_class')

card_row3_3 = dbc.Card(

    dbc.CardBody(
        [
            html.P('Departments',className='title_card'),
            html.H5(id = 'second_stores',className = 'value_card'),
            html.Sub(id = 'second_month_3',className='month_card')
        ]
    )

,className='card_class')

# determine the Navbar

navbar = dbc.NavbarSimple(
    children=[
            dcc.Dropdown(id='base_month',
                         options = month_unique,
                         value = '',
                         style = {'width':'300px'},
                         placeholder='Choose First Month',
                         clearable=True,),
            dcc.Dropdown(id ='reference_month',
                         options=month_unique,
                         value='',
                         style={'width':'300px','margin-left':'10px','margin-right':'1%'},
                         placeholder='Choose Second Month',
                         clearable=True),
            html.Div([
                html.Button("Data", id="btn_csv",style={'width':'100px','margin-left':'1%','border-radius':'100%','backgroundColor':'#010915',}),
                dcc.Download(id="download-dataframe-csv"),
            ],className='download'),




        ],
    brand="Monthly Comparison of Sales ",
    color="primary",
    dark=True,
    style={'height':'70px'}
)


# styling the tabs

tab_style = {'color':'#FFFFFF',
             'backgroundColor': '#484848',
              'fontSize':'0.8vw',
             'border-bottom': '1px solid white'}
selected_tab_style = {'color': '#000000',
                      'backgroundColor': '#909090',
                      'fontSize':'0.8vw',
                      'fontWeignt':'bold',
                      'border-top':'1px solid white',
                      'border-left':'1px solid white',
                      'border-right':'1px solid white'}

# define the tabs containing graphs and the card box

tab_data = html.Div([
 html.Div([
    dcc.Tabs(value='fig1', children=[
        dcc.Tab(fig1,
                label='Weekly Sales Comparison',
                style=tab_style,
                selected_style=selected_tab_style,
                value='fig1'),
        dcc.Tab(fig2,
                label='Stores level Sales Comparison' + '(Top 15)',
                style=tab_style,
                selected_style=selected_tab_style,
                value='fig2'
                ),
        dcc.Tab(fig3,
                label='Comparison of Sales between departments (Top 10)',
                style=tab_style,
                selected_style=selected_tab_style,
                value='fig3',
                ),
        dcc.Tab(fig4,
                label = 'Monthly Holiday Sales Comparison',
                style=tab_style,
                selected_style=selected_tab_style,
                value='fig4'),
        dcc.Tab(fig5,
                label = 'Monthly Sales comparison over the year',
                style = tab_style,
                selected_style=selected_tab_style,
                value = 'fig5')

    ]),
], style={'margin': '4%',
          'width': '60%',
          'display':'flex',
          'flex-direction':'column'}),

# creating container for cards

 html.Div([

     html.Div(children = [

         dbc.Container([



         dbc.Row([
             dbc.Col([card_row1_1]),
             dbc.Col([card_row1_2]),
             dbc.Col([card_row1_3]),
         ]),
             html.Br(),
             html.Br(),

         dbc.Row([
             dbc.Col([card_change1]),
             dbc.Col([card_change2]),
             dbc.Col([card_change3]),
         ]),
             html.Br(),
             html.Br(),

         dbc.Row([

                 dbc.Col([card_row3_1]),
                 dbc.Col([card_row3_2]),
                 dbc.Col([card_row3_3])
        ])

         ],fluid= True, style={'justify-content':'center'})
],className= 'card_data_inside')


 ],className= 'card_data_outside')


],className='main_container')

# defining the app layout

app.layout = html.Div(children = [navbar,tab_data])

# decorator and function

@app.callback(
    Output('week_line_chart1','figure'),
    Output('store_bar_graph1','figure'),
    Output('store_bar_graph2','figure'),
    Output('dept_funnel_graph1','figure'),
    Output('dept_funnel_graph2','figure'),
    Output('holiday_bar_graph1','figure'),
    Output('month_complete_year','figure'),
    Output('first_sales','children'),
    Output('first_month_1','children'),
    Output('second_sales','children'),
    Output('second_month_1','children'),
    Output('sales_change','children'),
    Output('first_holiday_sales','children'),
    Output('first_month_2','children'),
    Output('second_holiday_sale','children'),
    Output('second_month_2','children'),
    Output('holiday_sales_change','children'),
    Output('first_stores','children'),
    Output('first_month_3','children'),
    Output('second_stores','children'),
    Output('second_month_3','children'),
    Output('store_change','children'),




    Input('base_month','value'),
    Input('reference_month','value')
)

def update_graph(first_month,second_month):

    if first_month is None and second_month is None:
        raise dash.exceptions.PreventUpdate
    else:
        weekly_sale_first_month = weekly_sale[weekly_sale['Month'] == first_month].reset_index()
        weekly_sale_second_month = weekly_sale[weekly_sale['Month'] == second_month].reset_index()

# line graph for tab 1 - weekly sales comparison

        dict_line_tab_1 = {
           'data':[go.Scatter(
               x = weekly_sale_first_month['week_no'],
               y = weekly_sale_first_month['Weekly_Sales'],
               mode = 'text+markers+lines',
               text = weekly_sale_first_month['Weekly_Sales'].round(1),
               #texttemplate ='',
               marker=dict(color='#000000', size=12, symbol='circle',
                           line=dict(width=2, color='#FFFFFF')),
               textfont=dict(
                   family='sans-serif',
                   size=12,
                   color='white'),
               textposition='bottom right',
               line=dict(width=4, color='#318CE7'),
               hoverinfo='text',
               name = (first_month),
               hovertext=
               '<b>Month</b>:' + weekly_sale_first_month['Month'].astype(str) + '<br>' +
               '<b>Week Number</b>:' + weekly_sale_first_month['week_no'].astype(str) + '<br>' +
               '<b>Sales in the Week</b>:'+'$' + weekly_sale_first_month['Weekly_Sales'].round(1).astype(str) +'M'+ '<br>'
           ),
               go.Scatter(
                   x=weekly_sale_second_month['week_no'],
                   y=weekly_sale_second_month['Weekly_Sales'],
                   mode='text+markers+lines',
                   text= weekly_sale_second_month['Weekly_Sales'].round(1),
                   texttemplate='',
                   marker=dict(color='#000000', size=9, symbol='square',
                               line=dict(width=2, color='#FFFFFF')),
                   textfont=dict(
                       family='sans-serif',
                       size=12,
                       color='white'),
                   textposition='bottom right',
                   line=dict(width=4, color='#DC143C'),
                   name = second_month,
                   hoverinfo='text',
                   hovertext=
                   '<b>Month</b>:' + weekly_sale_second_month['Month'].astype(str) + '<br>' +
                   '<b>Week Number</b>:' + weekly_sale_second_month['week_no'].astype(str) + '<br>' +
                   '<b>Sales in the Week</b>:'+'$'+ + weekly_sale_second_month['Weekly_Sales'].round(1).astype(str)+'M' + '<br>'
               )
           ],
           'layout': go.Layout(
            plot_bgcolor = '#282828',
            paper_bgcolor ='#282828',
            hovermode='closest',
            xaxis = dict(
                title = '<b>Week No</b>',
                visible = True,
                color = 'white',
                showline = True,
                showgrid = False,
                showticklabels = True,
                linecolor = 'white',
                linewidth  = 1,
                ticks = 'outside',
                tickfont = dict(
                    family = 'Arial',
                    size = 12,
                    color = 'white'),
                tickmode = 'array',
                tickvals = [1, 2, 3, 4, 5],
                ticktext = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
            ),
               yaxis=dict(
                   title='<b>Weekly Sales in $ Millions </b>',
                   visible=True,
                   color='white',
                   showline=False,
                   showgrid=True,
                   showticklabels=True,
                   linecolor='white',
                   linewidth=1,
                   ticks='',
                   tickfont=dict(
                       family='Arial',
                       size=12,
                       color='white'),
                   tickprefix='$',
                   ticksuffix='M',

               ),
               margin=dict(t=20, r=20),
               legend=dict(bgcolor='grey')
           ),
       }
# store comparison tab 2
        store_first_month = store_df[store_df['Month']==first_month]
        store_first_ascending  = store_first_month.sort_values('Weekly_Sales',ascending=False)
        store_first = store_first_ascending[:15]

        store_second_month = store_df[store_df['Month']==second_month]
        store_second_ascending = store_second_month.sort_values('Weekly_Sales',ascending = False)
        store_second = store_second_ascending[:15]


        dict_bar_tab_2_g1 = {
            'data':[go.Bar(
                x = store_first['Weekly_Sales'],
                y = store_first['Store'],
                orientation='h',
                text = '$'+store_first['Weekly_Sales'].round(1).astype(str)+'M',
                textposition='auto',
                name = first_month,
                marker_color=store_first['Weekly_Sales'],
                #mode='text+markers',
                #texttemplate='',
                hoverinfo='text',
                hovertext='<b>Month:</b>:' + store_first['Month'].astype(str) + '<br>' +
                   '<b>Store:</b>:' + store_first['Store'].astype(str) + '<br>' +
                   '<b>Sales:</b>:'+'$'+ + store_first['Weekly_Sales'].round(1).astype(str)+'M' + '<br>'
                ),
                ],
            'layout':go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin = dict(t= 25,r = 10),
                xaxis = dict(
                    tickprefix = '$',
                    ticksuffix = 'M',
                    title = '<b>Sale in $ Millions for Month: </b>'+f'<b>{first_month}</b>',
                    visible = True,
                    showline = True,
                    showgrid = False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor = 'white',
                    linewidth = 1,
                    ticks = 'outside',
                    showticklabels = True,
                    color = 'white',
                    ),
                yaxis=dict(
                    title='<b>Store</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
            ),
        }

        dict_bar_tab_2_g2 = {
            'data': [go.Bar(
                    x=store_second['Weekly_Sales'],
                    y=store_second['Store'],
                    orientation='h',
                    text='$'+store_second['Weekly_Sales'].round(1).astype(str)+'M',
                    textposition='auto',
                    name=second_month,
                    marker_color = store_second['Weekly_Sales'],
                    hoverinfo='text',
                    hovertext='<b>Month:</b>:' + store_second['Month'].astype(str) + '<br>' +
                        '<b>Store:</b>:' + store_second['Store'].astype(str) + '<br>' +
                        '<b>Sales:</b>:' + '$' + + store_second['Weekly_Sales'].round(1).astype(str) + 'M' + '<br>'
                )
            ],
            'layout': go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin=dict(t=25, r=10),
                colorscale= dict(diverging=[[0, 'blue'], [0.5, 'yellow'], [1.0, 'rgb(0, 0, 255)']],
                                 sequential = 'blues',
                                 sequentialminus = 'bupu'),
                #go.layout.Colorscale('grey'),
                xaxis=dict(
                    tickprefix='$',
                    ticksuffix='M',
                    title='<b>Sale in $ Millions for Month: </b>'+f'<b>{second_month}</b>',
                    visible=True,
                    showline=True,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
                yaxis=dict(
                    title='<b>Store</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
            ),
        }

# department comparison tab 3

        no_of_unique_departments = len(dept_df['Dept'].unique())  # it's value is 81 [Not in Use] no of stores if 45 [Not in Use]

        dept_first_month = dept_df[dept_df['Month'] == first_month]
        dept_first_month_ascending = dept_first_month.sort_values('Weekly_Sales',ascending=False)
        dept_first = dept_first_month_ascending[:10]

        dept_second_month = dept_df[dept_df['Month'] == second_month]
        dept_second_month_ascending = dept_second_month.sort_values('Weekly_Sales',ascending=False)
        dept_second = dept_second_month_ascending[:10]

        dict_funnel_tab_3_g1 = {
            'data':[go.Funnel(
                x = dept_first['Weekly_Sales'],
                y = dept_first['Dept'],
                #text=dept_first['Weekly_Sales'],
                textposition='inside',
                name=first_month,
                marker = {'color':px.colors.sequential.Plotly3},
                hoverinfo='text',
                hovertext='<b>Month:</b>:' + dept_first['Month'].astype(str) + '<br>' +
                        '<b>Department:</b>:' + dept_first['Dept'].astype(str) + '<br>' +
                        '<b>Sales:</b>:' + '$' + + dept_first['Weekly_Sales'].round(1).astype(str) + 'M' + '<br>',
                connector = {'line':{'width':0},'visible':False}

            ),

            ],
            'layout':go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin=dict(t=25, r=10),
                #colorscale= dict(diverging=[[0, 'blue'], [0.5, 'yellow'], [1.0, 'rgb(0, 0, 255)']],
                                #sequential = 'blues',
                                #sequentialminus = 'bupu'),
                #go.layout.Colorscale('grey'),
                xaxis=dict(
                    tickprefix='$',
                    ticksuffix='M',
                    title='<b>Sale in $ Millions for Month : </b>'+f'<b>{first_month}</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=False,
                    color='white',
                ),
                yaxis=dict(
                    title='<b>Department</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
            ),

        }

        dict_funnel_tab_3_g2 = {
            'data': [go.Funnel(
                x=dept_second['Weekly_Sales'],
                y=dept_second['Dept'],
                textposition='inside',
                name=second_month,
                marker={'color': px.colors.sequential.Plotly3},
                hoverinfo='text',
                hovertext='<b>Month:</b>:' + dept_second['Month'].astype(str) + '<br>' +
                        '<b>Department:</b>:' + dept_second['Dept'].astype(str) + '<br>' +
                        '<b>Sales:</b>:' + '$' + + dept_second['Weekly_Sales'].round(1).astype(str) + 'M' + '<br>',
                connector={'line': {'width': 0},'visible':False}
            ),
            ],
            'layout': go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin=dict(t=25, r=10),
                xaxis=dict(
                    tickprefix='$',
                    ticksuffix='M',
                    title='<b>Sale in $ Millions for Month : </b>' + f'<b>{second_month}</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='',
                    showticklabels=False,
                    color='white',
                ),
                yaxis=dict(
                    title='<b>Department</b>',
                    visible=True,
                    showline=False,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
            ),

        }

        dict_bar_tab_4 = {
            'data': [go.Bar(
                    x=holiday_sales['Month'],
                    y=holiday_sales['Holiday_Sales'],
                    text='$'+holiday_sales['Holiday_Sales'].round(1).astype(str)+'M',
                    textposition='auto',
                    #name=first_month,
                    marker_color = holiday_sales['Holiday_Sales'],
                    marker={'line': {'color': 'white', 'width': 1.5, },'color': px.colors.sequential.Plotly3},
                    hoverinfo = 'text',
                    hovertext='<b>Month: </b>' + holiday_sales['Month'].astype(str) + '<br>' +
                              '<b>Holiday Sale Value: </b>' + '$' + holiday_sales['Holiday_Sales'].round(1).astype(str) + 'M' + '<br>'
            )
                ],
            'layout': go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin=dict(t=25, r=10),
                xaxis=dict(
                    #tickprefix='$',
                    #ticksuffix='M',
                    title='<b>Months with Holiday Sales</b>',
                    visible=True,
                    showline=True,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
                yaxis=dict(
                    title='<b>Holiday Sale in $ Millions</b>',
                    visible=True,
                    showline=False,
                    showgrid=True,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                    tickprefix='$',
                    ticksuffix='M',
                )
            )


        }

        dict_bar_tab_5 = {
            'data': [go.Bar(
                x=monthly_sales['Month'],
                y=monthly_sales['Weekly_Sales'],
                text='$'+monthly_sales['Weekly_Sales'].round(1).astype(str)+'M',
                textposition='inside',
                showlegend=False,
                marker_color=monthly_sales['Weekly_Sales'],
                marker={'autocolorscale':False,'line':{'color':'white','width':1.5,},'color':px.colors.sequential.Plotly3},
                hoverinfo='text',
                hovertext='<b>Month: </b>'+monthly_sales['Month'].astype(str)+'<br>'+
                          '<b>Sale Value: </b>'+'$'+monthly_sales['Weekly_Sales'].round(1).astype(str)+'M'+'<br>'
            ),

                go.Scatter(
                    x = monthly_sales_dates_mean['Month'],
                    y = monthly_sales_dates_mean['mean_weekly_sale_for_month'],
                    mode = 'markers+lines',
                    name = 'Mean Weekly Sales over the month',
                    line = dict(shape = 'spline',
                                smoothing = 1.3,
                                width = 4,
                                color = 'yellow',
                                ),
                    marker = dict(color = 'orange',size = 12,symbol = 'circle',line = dict(color = 'black',width = 1.5)),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext='<b>Month: </b>'+monthly_sales_dates_mean['Month'].astype(str)+'<br>'+
                              '<b>Mean Weekly Sale: </b>'+'$'+monthly_sales_dates_mean['mean_weekly_sale_for_month'].round(1).astype(str)+'M'+'<br>'
                )
            ],
            'layout': go.Layout(
                plot_bgcolor='#282828',
                paper_bgcolor='#282828',
                legend=dict(bgcolor='grey'),
                margin=dict(t=45, r=10,l=50),
                title='Monthly Sale Value and Mean Weekly Sale',
                titlefont=dict(
                        family='Arial',
                        size=20,
                        color='white'),
                # colorscale= dict(diverging=[[0, 'blue'], [0.5, 'yellow'], [1.0, 'rgb(0, 0, 255)']],
                #                 sequential = 'blues',
                #                 sequentialminus = 'bupu'),
                # go.layout.Colorscale('grey'),
                xaxis=dict(
                    # tickprefix='$',
                    # ticksuffix='M',
                    title='<b>Months</b>',
                    visible=True,
                    showline=True,
                    showgrid=False,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                ),
                yaxis=dict(
                    #title='<b>Monthly Sale value [BARS]  and <br> Mean Weekly Sale [LINE]</b>',
                    visible=True,
                    showline=False,
                    showgrid=True,
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='white'),
                    linecolor='white',
                    linewidth=1,
                    ticks='outside',
                    showticklabels=True,
                    color='white',
                    tickprefix='$',
                    ticksuffix='M',
                )
            )

        }
# sales calculation

        card_top_sales = '$ '+monthly_sales[monthly_sales['Month']==first_month]['Weekly_Sales'].round(1).astype(str)+' M'
        card_bottom_sales = '$ '+monthly_sales[monthly_sales['Month']==second_month]['Weekly_Sales'].round(1).astype(str)+' M'

        s1 = monthly_sales_df.loc[monthly_sales['Month']==first_month].reset_index()['Weekly_Sales'].round(1)
        s2 = monthly_sales_df.loc[monthly_sales['Month']==second_month].reset_index()['Weekly_Sales'].round(1)

        sc = ((s2-s1).round(1)).fillna(' ')

        sc_str = '$ '+sc.astype(str)+' M'


#holiday sales calculation

        holi_first = monthly_sales_df.loc[monthly_sales_df['Month'] == first_month].reset_index()['Holiday_Sales']
        holi_first_str = '$ '+monthly_sales_df.loc[monthly_sales_df['Month'] == first_month]['Holiday_Sales'].astype(str)+' M'
        holi_second = monthly_sales_df.loc[monthly_sales_df['Month'] == second_month].reset_index()['Holiday_Sales']
        holi_second_str = '$ '+ monthly_sales_df.loc[monthly_sales_df['Month'] == second_month].reset_index()['Holiday_Sales'].astype(str) +' M'

        diff_holiday = np.round(holi_second - holi_first, 1).fillna('~')
        diff_holiday_str = '$ ' + diff_holiday.astype(str) + ' M' if diff_holiday is not None else '-'

# department calculation

        dept_1 = len(dept_df[dept_df['Month']==first_month]['Dept'].unique())
        dept_2 = len(dept_df[dept_df['Month']==second_month]['Dept'].unique())

        dept_change = dept_2 - dept_1

        return dict_line_tab_1,dict_bar_tab_2_g1,dict_bar_tab_2_g2,dict_funnel_tab_3_g1,dict_funnel_tab_3_g2,dict_bar_tab_4,dict_bar_tab_5,card_top_sales,first_month,card_bottom_sales,second_month,sc_str,holi_first_str,first_month,holi_second_str,second_month,diff_holiday_str,dept_1,first_month,dept_2,second_month,dept_change


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_data(n_clicks):
    return dcc.send_data_frame(retail.to_csv, "sales-data.csv")



if __name__ == '__main__':
    app.run_server(debug = True)

