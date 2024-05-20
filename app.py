from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, FileField, DateField
from wtforms.validators import DataRequired, NumberRange, Email
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = 'static/images'

# Load tours data
if os.path.exists('tours.json'):
    with open('tours.json', 'r', encoding='utf-8') as f:
        tours = json.load(f)
else:
    tours = []

# Load bookings data
if os.path.exists('bookings.json'):
    with open('bookings.json', 'r', encoding='utf-8') as f:
        bookings = json.load(f)
else:
    bookings = []

# Form for adding new tours
class TourForm(FlaskForm):
    image = FileField('Tour Image', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])

# Form for booking tours
class BookingForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    tour_dates = DateField('Tour Dates', validators=[DataRequired()], format='%Y-%m-%d')
    email = StringField('Email', validators=[DataRequired(), Email()])

@app.route('/')
def index():
    return render_template('index.html', tours=tours)

@app.route('/add_tours', methods=['GET', 'POST'])
def add_tours():
    form = TourForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        tour = {
            'id': len(tours) + 1,
            'image': url_for('static', filename='images/' + filename),
            'description': form.description.data,
            'price': float(form.price.data)
        }
        tours.append(tour)
        with open('tours.json', 'w', encoding='utf-8') as f:
            json.dump(tours, f, ensure_ascii=False, indent=4)
        flash('Tour added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_tours.html', form=form)

@app.route('/show_tour/<int:tour_id>')
def show_tour(tour_id):
    tour = next((tour for tour in tours if tour['id'] == tour_id), None)
    if tour:
        return render_template('show_tour.html', tour=tour)
    else:
        return "Tour not found", 404

@app.route('/form_tour/<int:tour_id>', methods=['GET', 'POST'])
def form_tour(tour_id):
    tour = next((tour for tour in tours if tour['id'] == tour_id), None)
    if not tour:
        return "Tour not found", 404

    form = BookingForm()
    if form.validate_on_submit():
        booking = {
            'tour_id': tour_id,
            'full_name': form.full_name.data,
            'tour_dates': form.tour_dates.data.strftime('%Y-%m-%d'),
            'email': form.email.data
        }
        bookings.append(booking)
        with open('bookings.json', 'w', encoding='utf-8') as f:
            json.dump(bookings, f, ensure_ascii=False, indent=4)
        flash('Забронировано удачно!', 'success')
        return redirect(url_for('index'))

    return render_template('form_tour.html', tour=tour, form=form)

if __name__ == '__main__':
    app.run(debug=True)
