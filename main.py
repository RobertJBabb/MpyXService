import os
import subprocess
import uuid
from flask import Flask, after_this_request
from flask import render_template, request, flash, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads' # relative path
ALLOWED_EXTENSIONS = {'txt', 'py'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
# Set the secret key to some random bytes. Change this!
app.secret_key = b'Put your secret key here'

@app.route('/')
def base_redirect():
    return redirect('/mpycross')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def run_mpy_cross(filenamep, opts):
    result = {'filenameo': None, 'errorcode': None, 'output': None}
    filenameo = ""
    try:
        filenameo = os.path.basename(filenamep).rsplit('.', 1)[0]
        filenameup = filenameo + '.mpy'
        filenameo = os.path.join(app.config['UPLOAD_FOLDER'], filenameup)
        opts_str = ''
        for myopt in opts:
            if myopt == 'CacheMapLookup':
                opts_str += ' -mcache-lookup-bc'
            elif myopt == 'noUnicode':
                opts_str += ' -mno-unicode'
            elif myopt == 'SmallIntBits':
                opts_str += ' -msmall-int-bits={}'.format(opts[myopt])
            elif myopt == 'emit':
                opts_str += ' -X emit={}'.format(opts[myopt])
            elif myopt == 'optLevel':
                opts_str += ' -O{}'.format(opts[myopt])

        cmd = 'python -m mpy_cross -v{} {} -o {}'.format(opts_str, filenamep, filenameo)
        result_sub = subprocess.check_output(
            [cmd], shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        os.remove(filenamep)
    except subprocess.CalledProcessError as e:
        result['errorcode'] = e.returncode
        result['output'] = e.output
        try:
            os.remove(filenamep)
            os.remove(filenameo)
        except:
            pass
        return result
    try:
        os.stat(filenameo)
    except FileNotFoundError as e:
        flash("mpy-cross output {}: not found".format(filenameo))
        filenameup = None
    result['filenameo'] = filenameup
    return result


@app.route('/mpycross', methods=['GET', 'POST'])
def upload_file():
    error = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file specified: Please select a file')
            return redirect(request.url)
        file = request.files['file']
        # Gather options settings
        mpy_opts = {}
        if request.form.get('emit_select') != 'default':
            mpy_opts['emit'] = request.form.get('emit_select')
        noUnicodeOpt = request.form.get('NoUnicode')
        if noUnicodeOpt:
            mpy_opts['noUnicode'] = True
        CacheMapLookupsOpt = request.form.get('CacheBC')
        if CacheMapLookupsOpt:
            mpy_opts['CacheMapLookup'] = True
        SmallIntOpt = request.form.get('SetIntBits')
        if SmallIntOpt:
            SmallIntBitsVal = request.form.get('SmallIntBits')
            mpy_opts['SmallIntBits'] = SmallIntBitsVal

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Get UUID to make filename unique
            fuuid = uuid.uuid1()
            filename = fuuid.hex + '.' + filename
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_filename)
            mpyx_result = run_mpy_cross(full_filename, mpy_opts)
            if mpyx_result['filenameo']:
                return redirect(url_for('uploaded_file',
                                        filename=mpyx_result['filenameo']))
            else:
                return render_template('uploaderror.html', messages={'error': mpyx_result['errorcode'],
                                                                     'output': mpyx_result['output']})
        else:
            flash('Unsupported file type')
            return "mpy_cross failed"
    return render_template('get_py_file.html', error=error)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    @after_this_request
    def remove_file(response):
        filenamer = './uploads/{}'.format(filename)
        try:
            os.remove(filenamer)
        except Exception as error:
            print('Error removing: {}'.format(filenamer))
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response

    up_filename = os.path.basename(filename)
    # Strip off UUID to get save filename
    s_filename = ".".join(up_filename.rsplit('.')[1:])
    return send_from_directory(app.config['UPLOAD_FOLDER'], up_filename, as_attachment=True, attachment_filename=s_filename)

