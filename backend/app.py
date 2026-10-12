import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from .models import db, User, Car, Booking
except ImportError:
    from models import db, User, Car, Booking


app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)
app.config['SECRET_KEY'] = '12345'  # Replace with a secure secret key



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



with app.app_context():
    db.create_all()
    if Car.query.count() == 0:
        sample_cars = [
            Car(name='Maruti Alto', price_per_day=60),
            Car(name='Hyundai Santro', price_per_day=65),
            Car(name='Tata Tiago', price_per_day=70),
            Car(name='Renault Kwid', price_per_day=55),
            Car(name='Volkswagen Polo', price_per_day=75),
            Car(name='Honda Amaze', price_per_day=80),
            Car(name='Ford Figo', price_per_day=70),
            Car(name='Maruti Celerio', price_per_day=60),
            Car(name='Hyundai Grand i10', price_per_day=75),
            Car(name='Tata Tigor', price_per_day=70)
        ]
        db.session.bulk_save_objects(sample_cars)
        db.session.commit()



@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('register'))



@app.route('/home')
@login_required
def home():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', username=current_user.username, bookings=user_bookings)



@app.route('/api/cars')
@login_required
def get_cars():
    cars = Car.query.all()
    return jsonify({'cars': [{'id': c.id, 'name': c.name, 'price': c.price_per_day} for c in cars]})



@app.route('/api/book', methods=['POST'])
@login_required
def book_car():
    data = request.json
    car_id = data.get('car_id')
    days = data.get('days')
    kilometers = data.get('kilometers')



    if not car_id or not days or not kilometers:
        return jsonify({'message': 'Missing booking information'}), 400



    car = Car.query.get(car_id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404



    price_per_km = 1.5
    total_price = (car.price_per_day * days) + (price_per_km * kilometers)
    receipt_number = str(uuid.uuid4())
    booking = Booking(user_id=current_user.id, car_id=car_id, days=days,
                      total_price=total_price, kilometers=kilometers,
                      receipt_number=receipt_number)
    db.session.add(booking)
    db.session.commit()



    return jsonify({
        'message': 'Booking successful',
        'booking': {
            'id': booking.id,
            'car_name': car.name,
            'user_name': current_user.username,
            'days': days,
            'kilometers': kilometers,
            'total_price': total_price,
            'receipt_number': receipt_number
        }
    })



@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("You don't have permission to pay for this booking.")
        return redirect(url_for('home'))



    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        booking.is_paid = True
        db.session.commit()
        flash(f"Payment successful via {payment_method} for booking of {booking.car.name}.")
        return redirect(url_for('home'))



    return render_template('payment.html', booking=booking)



@app.route('/cancel_booking', methods=['GET', 'POST'])
@login_required
def cancel_booking_page():
    if request.method == 'POST':
        receipt_number = request.form.get('receipt_number')
        booking = Booking.query.filter_by(receipt_number=receipt_number, user_id=current_user.id).first()
        if booking:
            refund_amount = booking.total_price if booking.is_paid else 0
            db.session.delete(booking)
            db.session.commit()
            flash(f'Booking canceled successfully. Refund amount: ${refund_amount:.2f}')
            return redirect(url_for('home'))
        else:
            flash('Invalid receipt number or booking not found.')
            return redirect(url_for('cancel_booking_page'))



    return render_template('cancel_booking.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
