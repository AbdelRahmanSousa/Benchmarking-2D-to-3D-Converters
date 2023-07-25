import os
from subprocess import check_output
from dash import Dash
from dash.dependencies import Input, Output, State
from FloorplanToBlender3d.FloorplanToBlenderLib import *
import dash_html_components as html
import dash_core_components as cc
import dash_bio


# ---------------------------------For 3d reconstruction---------------------------------
'''reconstructionModels = []
files = os.scandir("./3d_reconstruction")
for entry in files:
    if entry.is_file():
        fileName = entry.name.split('.')
        if fileName[0].lower() != 'model' and fileName[-1] == 'py':
            reconstructionModels.append(fileName[0])'''
# ---------------------------------Upload element markup---------------------------------
uploadDiv = html.Div(
    ['Drag and Drop or ',
     html.A('Select Files')
     ],
    style={
        'width': '100%',
        'height': '30%',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    }
)
# ---------------------------------App layout---------------------------------
app = Dash(name='Floor Plan 3D Converter')
app.layout = html.Div([html.H1('Upload Plan'),
                       cc.Dropdown(options=[x[1:] for x in const.SUPPORTED_BLENDER_FORMATS], value=None,
                                   placeholder='Export format', id='export_type'),
                       cc.Upload(uploadDiv, id='plan'),
                       html.Button('Download', id='download_btn', n_clicks=0)
                       ])


# --------------------------Callbacks--------------------------
@app.callback(Input('download_btn', 'n_clicks'), State('plan', 'contents'), State('plan', 'filename'), State('export_type', 'value'))
def convert_plan(uploaded_contents, out_format):
    # Create image file and floor plan config
    image_name = ''
    # Parse configuration from system.ini
    blender_install_path = config.get('/Config/system.ini', 'SYSTEM', const.STR_BLENDER_INSTALL_PATH)
    target_base = config.get('/Config/system.ini', 'SYSTEM', const.STR_OUTPUT_FOLDER) + "\\" + config.get('/Config/system.ini', 'SYSTEM', const.STR_OUTPUT_NAME)
    target_path = target_base + const.BASE_FORMAT
    target_path = IO.get_next_target_base_name(target_base, target_path) + const.BASE_FORMAT
    program_path = config.get('/Config/system.ini', 'SYSTEM', const.STR_PROGRAM_PATH)
    # Create floor plan & execute feature extractor
    fp = floorplan.new_floorplan('/Config/default.ini')
    fp.image_path = image_name
    data_paths = execution.simple_single(fp)
    # Execute Blender scripts
    check_output(
        [
            blender_install_path,
            "-noaudio",  # this is a dockerfile ubuntu hax fix
            "--background",
            "--python",
            config.get('/Config/system.ini', 'SYSTEM', const.STR_BLENDER_SCRIPT_CREATE_PATH),
            program_path,  # Send this as parameter to script
            target_path,
        ]
        + data_paths
    )
    if out_format != 'blend':
        check_output(
            [
                blender_install_path,
                "--background",
                target_path,
                "--python",
                config.get('/Config/system.ini', 'SYSTEM', const.STR_BLENDER_SCRIPT_EXPORT_PATH),
                target_path,
                '.' + out_format,
                target_base + out_format,
            ]
        )
    return None


@app.callback(Output('', '2dModel'), Input('', '2dModel'))
def model_uploaded():
    pass


if __name__ == '__main__':
    app.run_server(port=4050)
'''html.H1('Choose Model Converter'),
                       cc.Dropdown(options=reconstructionModels,
                                   value=None, placeholder='2D To 3D Converter',
                                   id='model_name'),
                       html.H1('Upload Models'),
                       cc.Upload(uploadDiv, id='2dModel', multiple=True)'''
