from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Your home page

@app.route('/comand')
def comand():
    return render_template('comand.html')  # New Drone Command page

@app.route('/track', methods=['POST'])
def track():
    # Logic to handle the form submission for tracking
    latitude = request.form.get('lat')
    longitude = request.form.get('lon')
    # Process coordinates as needed...
    print(f"Received coordinates: Latitude {latitude}, Longitude {longitude}")
    
    return redirect(url_for('home'))  # Redirect after processing

@app.route('/command')
def command():
    # Define what this route should render
    return render_template('command.html')  # Create this command.html template

if __name__ == '__main__':
    app.run(debug=True)
