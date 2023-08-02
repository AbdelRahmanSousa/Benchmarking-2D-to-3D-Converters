import base64
import os
import uuid
from subprocess import check_output
from dash import Dash
from dash.dependencies import Input, Output, State
from FloorplanToBlenderLib import *
import dash_html_components as html
import dash_core_components as cc
from reconstruction.Pix2Vox import Pix2Vox
import dash_bio
from dash.exceptions import PreventUpdate

# ---------------------------------For 3d reconstruction---------------------------------
'''reconstructionModels = []
files = os.scandir("./reconstruction")
for entry in files:
    if entry.is_file():
        fileName = entry.name.split('.')
        if fileName[0].lower() != 'model' and fileName[0].lower() != '__init__' and fileName[-1] == 'py':
            reconstructionModels.append(fileName[0])'''
# ---------------------------------Upload element markup---------------------------------
uploadDiv = html.Div(
    ['Drag and Drop or ',
     html.A('Select Files')
     ],
    style={
        'width': '100%',
        'height': '6rem',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
    }
)
# ---------------------------------App layout---------------------------------
app = Dash(name='Floor Plan 3D Converter')

home = [html.H1('2D To 3D'), html.Button('Convert Plan', id='convert_plan', n_clicks_timestamp=0),
        html.Button('Convert 2D Model', id='convert_model', n_clicks_timestamp=0),
        html.Div(id='go_home', n_clicks_timestamp=0)]
step1 = [html.H1('Upload Plan'),
         cc.Dropdown(options=[x[1:] for x in const.SUPPORTED_BLENDER_FORMATS], value=None,
                     placeholder='Export format', id='export_type'),
         cc.Upload(uploadDiv, id='upload'),
         html.Button('Download', id='download_plan_btn'),
         cc.Download(id="download_plan"),
         html.Button('Back', id='go_home'),
         html.Div(id='convert_model', n_clicks_timestamp=0),
         html.Div(id='convert_plan', n_clicks_timestamp=0)]
step2 = [html.H1('Convert 2D Model'),
         cc.Upload(uploadDiv, id='upload', multiple=True),
         html.Button('Download', id='download_model_btn'),
         cc.Download(id="download_model"),
         html.Button('Back', 'go_home'),
         html.Div(id='convert_model', n_clicks_timestamp=0),
         html.Div(id='convert_plan', n_clicks_timestamp=0)
         ]
pages = [home, step1, step2]

app.layout = html.Div([cc.Store('current_page', data=-1),
                       html.Div(html.Img(src='./assets/logo.png', id='logo'), id='bar'),
                       html.Div(pages[0], id='container')], id='main',
                      style={'backgroundImage': 'url(assets/background.jpg)'})


# --------------------------Callbacks--------------------------
@app.callback(Output('upload', 'children'), Input('upload', 'contents'), [State('upload', 'filename')])
def change_upload_view(contents, files):
    uploaded_files = zip(contents, files)
    raise PreventUpdate()


@app.callback(Output('container', 'children'),
              [Input('convert_model', 'n_clicks_timestamp'),
               Input('convert_plan', 'n_clicks_timestamp'),
               Input('go_home', 'n_clicks_timestamp')
               ])
def goToPage(model_timestamp, plan_timestamp, home_timestamp):
    if model_timestamp == plan_timestamp == home_timestamp:
        raise PreventUpdate()
    if home_timestamp > plan_timestamp and home_timestamp > model_timestamp:
        return pages[0]
    elif plan_timestamp > model_timestamp:
        return pages[1]
    else:
        return pages[2]


@app.callback(Output('download_plan', 'data'),
              [Input('download_plan_btn', 'n_clicks')],
              [State('upload', 'contents'),
               State('upload', 'filename'),
               State('export_type', 'value')])
def convert_plan(n_clicks, uploaded_contents, file_name, out_format):
    if file_name is None or uploaded_contents is None or out_format is None:
        raise PreventUpdate()
    # Create image file and floor plan config
    image_name = './Data/' + file_name
    image_file = open(image_name, 'wb+')
    image_file.write(base64.b64decode(uploaded_contents.split(',')[1]))
    image_file.close()
    # Parse configuration from system.ini
    blender_install_path = config.get('./Config/system.ini', 'SYSTEM', const.STR_BLENDER_INSTALL_PATH)
    target_base = config.get('./Config/system.ini', 'SYSTEM', const.STR_OUTPUT_FOLDER) + str(uuid.uuid4())
    target_path = target_base + const.BASE_FORMAT
    target_path = IO.get_next_target_base_name(target_base, target_path) + const.BASE_FORMAT
    program_path = config.get('./Config/system.ini', 'SYSTEM', const.STR_PROGRAM_PATH)
    # Create floor plan & execute feature extractor
    fp = floorplan.new_floorplan('./Config/default.ini')
    fp.image_path = image_name
    data_paths = execution.simple_single(fp)
    # Execute Blender scripts
    check_output(
        [
            blender_install_path,
            "-noaudio",  # this is a dockerfile ubuntu hax fix
            "--background",
            "--python",
            config.get('./Config/system.ini', 'SYSTEM', const.STR_BLENDER_SCRIPT_CREATE_PATH),
            program_path,  # Send this as parameter to script
            target_path,
        ]
        + [data_paths]
    )
    export_path = None
    export_base = None
    drive, s = os.path.splitdrive(target_path)
    if not drive:
        export_path = program_path + target_path
        export_base = program_path + target_base
    else:
        export_path = target_path
        export_base = target_base
    if out_format != 'blend':
        check_output(
            [
                blender_install_path,
                "--background",
                export_path,
                "--python",
                config.get('./Config/system.ini', 'SYSTEM', const.STR_BLENDER_SCRIPT_EXPORT_PATH),
                export_path,
                '.' + out_format,
                export_base + '.' + out_format,
            ]
        )
    # Clean up
    IO.clean_data_folder(const.BASE_PATH)
    # TODO clean up exported file
    return cc.send_file(export_base + '.' + out_format)


# Create Constructor Model instance
reconstructor = Pix2Vox('./pretrained_models/Pix2Vox')


@app.callback(Output('download_model', 'data'),
              [Input('download_model_btn', 'n_clicks')],
              [State('upload', 'contents'),
               State('upload', 'filename')])
def convert_model(n_clicks, uploaded_contents, file_names):
    if uploaded_contents is None or file_names is None:
        raise PreventUpdate()
    image_paths = []
    # Save uploaded files
    for img, img_name in zip(uploaded_contents, file_names):
        image_name = './Data/' + img_name
        image_file = open(image_name, 'wb+')
        image_file.write(base64.b64decode(img.split(',')[1]))
        image_file.close()
        image_paths.append(image_name)
    # Pass path array to model to convert
    model = reconstructor.convert(image_paths)
    # Return converted model
    return cc.send_file(model)


if __name__ == '__main__':
    app.run_server(port=4050)
