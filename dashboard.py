import dash
import dash_html_components as html
import dash_core_components as cc
app = dash.Dash()
app.layout = html.Div(html.H1('Upload Plan'))
if __name__ == '__main__':
    app.run_server(port=4050)
