fetch('/api/cars')
.then(res => {
    if (!res.ok) throw new Error('Failed to load cars');
    return res.json();
})
.then(data => {
    const carList = document.getElementById('car-list');
    const carSelect = document.getElementById('car-select');
    if (!carList || !carSelect) {
      console.error('Required elements not found.');
      return;
    }
    data.cars.forEach(car => {
        const div = document.createElement('div');
        div.textContent = `${car.name} - $${car.price}/day`;
        carList.appendChild(div);

        const option = document.createElement('option');
        option.value = car.id;
        option.textContent = `${car.name} ($${car.price}/day)`;
        carSelect.appendChild(option);
    });
})
.catch(error => {
    alert('Could not load car list.');
    console.error(error);
});

document.getElementById('booking-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const carId = parseInt(document.getElementById('car-select').value);
    const days = parseInt(document.getElementById('days').value);
    const kilometers = parseInt(document.getElementById('kilometers').value);
    const messageDiv = document.getElementById('message');

    if (!carId || !days || !kilometers) {
        messageDiv.style.color = 'red';
        messageDiv.textContent = 'Please fill all booking details correctly.';
        return;
    }

    fetch('/api/book', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({car_id: carId, days: days, kilometers: kilometers})
    })
    .then(res => {
        if (!res.ok) throw new Error('Booking failed');
        return res.json();
    })
    .then(data => {
        if(data.message === 'Booking successful') {
            messageDiv.style.color = 'green';
            messageDiv.textContent = `Booking confirmed for ${data.booking.car_name} for ${data.booking.days} day(s), ${data.booking.kilometers} km travel. Total price: $${data.booking.total_price.toFixed(2)}. Receipt Number: ${data.booking.receipt_number}`;

            setTimeout(() => {
                window.location.href = `/payment/${data.booking.id}`;
            }, 3000);
        } else {
            messageDiv.style.color = 'red';
            messageDiv.textContent = data.message || 'Booking failed';
        }
    })
    .catch(error => {
        messageDiv.style.color = 'red';
        messageDiv.textContent = 'Network or server error. Please try again.';
        console.error(error);
    });
});
