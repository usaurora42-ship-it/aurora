# import all libraires
import os
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'templates/uploads'

# Create upload_image function for upload and return files
@app.route('/', methods=['GET', 'POST'])
def upload_image():
	if request.method == 'POST':
		file = request.files['file']
		print("file name")
		print(file.filename)
		file.save(os.path.join(app.config['UPLOAD_PATH'], file.filename))
		return f'Uploaded: {file.filename}'
	return render_template('products/products.html')


