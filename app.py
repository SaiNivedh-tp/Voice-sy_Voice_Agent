# app.py

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid
from functools import wraps
import json

app = Flask(__name__)

users = {}
providers = {}
services = {}
appointments = {}
availability = {}

def generate_id():
    return str(uuid.uuid4())

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = token.replace('Bearer ', '')
        if user_id not in users:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.current_user = users[user_id]
        return f(*args, **kwargs)
    return decorated

# Initialize dummy data
def init_dummy_data():
    # Create dummy users
    user1_id = generate_id()
    user2_id = generate_id()
    
    users[user1_id] = {
        'id': user1_id,
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'created_at': datetime.now().isoformat()
    }
    
    users[user2_id] = {
        'id': user2_id,
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone': '+1234567891',
        'created_at': datetime.now().isoformat()
    }
    
    # Create dummy providers
    provider1_id = generate_id()
    provider2_id = generate_id()
    
    providers[provider1_id] = {
        'id': provider1_id,
        'name': 'Dr. Sarah Wilson',
        'specialty': 'Dermatology',
        'description': 'Board-certified dermatologist with 10+ years experience',
        'location': {
            'address': '123 Medical Center Dr',
            'city': 'New York',
            'state': 'NY',
            'zip': '10001'
        },
        'rating': 4.8,
        'reviews_count': 156,
        'image_url': 'https://example.com/dr-wilson.jpg',
        'created_at': datetime.now().isoformat()
    }
    
    providers[provider2_id] = {
        'id': provider2_id,
        'name': 'Luxury Spa & Wellness',
        'specialty': 'Beauty & Wellness',
        'description': 'Full-service spa offering massages, facials, and wellness treatments',
        'location': {
            'address': '456 Wellness Ave',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip': '90210'
        },
        'rating': 4.9,
        'reviews_count': 203,
        'image_url': 'https://example.com/spa.jpg',
        'created_at': datetime.now().isoformat()
    }
    
    # Create dummy services
    service1_id = generate_id()
    service2_id = generate_id()
    service3_id = generate_id()
    
    services[service1_id] = {
        'id': service1_id,
        'provider_id': provider1_id,
        'name': 'Skin Consultation',
        'description': 'Comprehensive skin assessment and treatment plan',
        'duration': 30,  # minutes
        'price': 150.00,
        'category': 'Consultation'
    }
    
    services[service2_id] = {
        'id': service2_id,
        'provider_id': provider2_id,
        'name': 'Deep Tissue Massage',
        'description': 'Therapeutic massage targeting muscle tension',
        'duration': 60,
        'price': 120.00,
        'category': 'Massage'
    }
    
    services[service3_id] = {
        'id': service3_id,
        'provider_id': provider2_id,
        'name': 'Anti-Aging Facial',
        'description': 'Rejuvenating facial treatment with premium products',
        'duration': 90,
        'price': 200.00,
        'category': 'Facial'
    }
    
    # Create availability slots
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for provider_id in [provider1_id, provider2_id]:
        availability[provider_id] = []
        
        # Create availability for next 14 days
        for day in range(14):
            current_date = base_date + timedelta(days=day)
            
            # Skip weekends for medical provider
            if provider_id == provider1_id and current_date.weekday() >= 5:
                continue
            
            # Create time slots (9 AM to 5 PM, 30-minute intervals)
            for hour in range(9, 17):
                for minute in [0, 30]:
                    slot_time = current_date.replace(hour=hour, minute=minute)
                    availability[provider_id].append({
                        'id': generate_id(),
                        'datetime': slot_time.isoformat(),
                        'available': True
                    })

# API Routes

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# User routes
@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'email', 'phone']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = generate_id()
    user = {
        'id': user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'created_at': datetime.now().isoformat()
    }
    
    users[user_id] = user
    
    return jsonify({
        'user': user,
        'token': user_id  # Simplified token (in production, use JWT)
    }), 201

@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email required'}), 400
    
    # Find user by email (simplified)
    user = next((u for u in users.values() if u['email'] == data['email']), None)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user,
        'token': user['id']
    })

@app.route('/users/profile', methods=['GET'])
@auth_required
def get_user_profile():
    return jsonify({'user': request.current_user})

# Provider routes
@app.route('/providers', methods=['GET'])
def get_providers():
    # Filter providers by specialty, location, etc.
    specialty = request.args.get('specialty')
    city = request.args.get('city')
    
    filtered_providers = list(providers.values())
    
    if specialty:
        filtered_providers = [p for p in filtered_providers 
                            if specialty.lower() in p['specialty'].lower()]
    
    if city:
        filtered_providers = [p for p in filtered_providers 
                            if city.lower() in p['location']['city'].lower()]
    
    return jsonify({'providers': filtered_providers})

@app.route('/providers/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    if provider_id not in providers:
        return jsonify({'error': 'Provider not found'}), 404
    
    provider = providers[provider_id]
    provider_services = [s for s in services.values() if s['provider_id'] == provider_id]
    
    return jsonify({
        'provider': provider,
        'services': provider_services
    })

# Service routes
@app.route('/services', methods=['GET'])
def get_services():
    provider_id = request.args.get('provider_id')
    
    if provider_id:
        filtered_services = [s for s in services.values() if s['provider_id'] == provider_id]
    else:
        filtered_services = list(services.values())
    
    return jsonify({'services': filtered_services})

@app.route('/services/<service_id>', methods=['GET'])
def get_service(service_id):
    if service_id not in services:
        return jsonify({'error': 'Service not found'}), 404
    
    return jsonify({'service': services[service_id]})

# Availability routes
@app.route('/providers/<provider_id>/availability', methods=['GET'])
def get_availability(provider_id):
    if provider_id not in providers:
        return jsonify({'error': 'Provider not found'}), 404
    
    date_str = request.args.get('date')  # Format: YYYY-MM-DD
    
    provider_availability = availability.get(provider_id, [])
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            provider_availability = [
                slot for slot in provider_availability
                if datetime.fromisoformat(slot['datetime']).date() == target_date
            ]
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    return jsonify({'availability': provider_availability})

# Appointment routes
@app.route('/appointments', methods=['POST'])
@auth_required
def create_appointment():
    data = request.get_json()
    
    required_fields = ['provider_id', 'service_id', 'datetime', 'notes']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate provider and service exist
    if data['provider_id'] not in providers:
        return jsonify({'error': 'Provider not found'}), 404
    
    if data['service_id'] not in services:
        return jsonify({'error': 'Service not found'}), 404
    
    # Check if slot is available
    provider_slots = availability.get(data['provider_id'], [])
    slot = next((s for s in provider_slots if s['datetime'] == data['datetime']), None)
    
    if not slot or not slot['available']:
        return jsonify({'error': 'Time slot not available'}), 400
    
    # Create appointment
    appointment_id = generate_id()
    appointment = {
        'id': appointment_id,
        'user_id': request.current_user['id'],
        'provider_id': data['provider_id'],
        'service_id': data['service_id'],
        'datetime': data['datetime'],
        'status': 'confirmed',
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat()
    }
    
    appointments[appointment_id] = appointment
    
    # Mark slot as unavailable
    slot['available'] = False
    
    # Include related data in response
    provider = providers[data['provider_id']]
    service = services[data['service_id']]
    
    return jsonify({
        'appointment': appointment,
        'provider': provider,
        'service': service
    }), 201

@app.route('/appointments', methods=['GET'])
@auth_required
def get_appointments():
    user_appointments = [
        apt for apt in appointments.values() 
        if apt['user_id'] == request.current_user['id']
    ]
    
    # Enrich with provider and service data
    enriched_appointments = []
    for apt in user_appointments:
        enriched_apt = apt.copy()
        enriched_apt['provider'] = providers[apt['provider_id']]
        enriched_apt['service'] = services[apt['service_id']]
        enriched_appointments.append(enriched_apt)
    
    return jsonify({'appointments': enriched_appointments})

@app.route('/appointments/<appointment_id>', methods=['GET'])
@auth_required
def get_appointment(appointment_id):
    if appointment_id not in appointments:
        return jsonify({'error': 'Appointment not found'}), 404
    
    appointment = appointments[appointment_id]
    
    # Check if user owns this appointment
    if appointment['user_id'] != request.current_user['id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Enrich with related data
    appointment['provider'] = providers[appointment['provider_id']]
    appointment['service'] = services[appointment['service_id']]
    
    return jsonify({'appointment': appointment})

@app.route('/appointments/<appointment_id>/cancel', methods=['POST'])
@auth_required
def cancel_appointment(appointment_id):
    if appointment_id not in appointments:
        return jsonify({'error': 'Appointment not found'}), 404
    
    appointment = appointments[appointment_id]
    
    # Check if user owns this appointment
    if appointment['user_id'] != request.current_user['id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update appointment status
    appointment['status'] = 'cancelled'
    appointment['cancelled_at'] = datetime.now().isoformat()
    
    # Make slot available again
    provider_slots = availability.get(appointment['provider_id'], [])
    slot = next((s for s in provider_slots if s['datetime'] == appointment['datetime']), None)
    if slot:
        slot['available'] = True
    
    return jsonify({'appointment': appointment})

@app.route('/appointments/<appointment_id>/reschedule', methods=['POST'])
@auth_required
def reschedule_appointment(appointment_id):
    if appointment_id not in appointments:
        return jsonify({'error': 'Appointment not found'}), 404
    
    appointment = appointments[appointment_id]
    
    # Check if user owns this appointment
    if appointment['user_id'] != request.current_user['id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data or 'datetime' not in data:
        return jsonify({'error': 'New datetime required'}), 400
    
    # Check if new slot is available
    provider_slots = availability.get(appointment['provider_id'], [])
    new_slot = next((s for s in provider_slots if s['datetime'] == data['datetime']), None)
    
    if not new_slot or not new_slot['available']:
        return jsonify({'error': 'New time slot not available'}), 400
    
    # Make old slot available
    old_slot = next((s for s in provider_slots if s['datetime'] == appointment['datetime']), None)
    if old_slot:
        old_slot['available'] = True
    
    # Update appointment and mark new slot as unavailable
    appointment['datetime'] = data['datetime']
    appointment['updated_at'] = datetime.now().isoformat()
    new_slot['available'] = False
    
    return jsonify({'appointment': appointment})

@app.route('/slots/suggest', methods=['GET'])
def suggest_slots():
    provider_id = request.args.get('provider_id')
    service_id = request.args.get('service_id')
    date_str = request.args.get('date')  # format: YYYY-MM-DD

    if not provider_id or provider_id not in providers:
        return jsonify({'error': 'Valid provider_id required'}), 400

    if not service_id or service_id not in services:
        return jsonify({'error': 'Valid service_id required'}), 400

    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    duration = services[service_id]['duration']
    provider_slots = availability.get(provider_id, [])

    suggested = []
    for slot in provider_slots:
        slot_time = datetime.fromisoformat(slot['datetime'])
        if slot['available'] and slot_time.date() == date:
            suggested.append(slot['datetime'])
        if len(suggested) >= 5:
            break

    return jsonify({
        'provider_id': provider_id,
        'service_id': service_id,
        'suggested_slots': suggested
    })

@app.route('/appointments/<appointment_id>/send-reminder', methods=['POST'])
def send_reminder(appointment_id):
    appointment = appointments.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    user = users.get(appointment['user_id'], {})
    service = services.get(appointment['service_id'], {})
    provider = providers.get(appointment['provider_id'], {})

    reminder_text = (
        f"Hello {user.get('name', 'Guest')}, this is a reminder for your "
        f"{service.get('name', 'appointment')} with {provider.get('name', 'the provider')} "
        f"at {appointment['datetime']}."
    )

    print(f"[VOICE REMINDER]: To {user.get('phone')} - {reminder_text}")

    return jsonify({
        'status': 'Reminder simulated',
        'reminder': reminder_text
    })

# Search route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    location = request.args.get('location', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    results = {
        'providers': [],
        'services': []
    }
    
    # Search providers
    for provider in providers.values():
        if (query in provider['name'].lower() or 
            query in provider['specialty'].lower() or 
            query in provider['description'].lower()):
            
            if not location or location in provider['location']['city'].lower():
                results['providers'].append(provider)
    
    # Search services
    for service in services.values():
        if (query in service['name'].lower() or 
            query in service['description'].lower() or 
            query in service['category'].lower()):
            
            provider = providers[service['provider_id']]
            if not location or location in provider['location']['city'].lower():
                service_with_provider = service.copy()
                service_with_provider['provider'] = provider
                results['services'].append(service_with_provider)
    
    return jsonify(results)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_dummy_data()
    print("Booking API Server Starting...")
    print("Available endpoints:")
    print("- POST /users/register")
    print("- POST /users/login")
    print("- GET /users/profile")
    print("- GET /providers")
    print("- GET /providers/<id>")
    print("- GET /services")
    print("- GET /providers/<id>/availability")
    print("- POST /appointments")
    print("- GET /appointments")
    print("- POST /appointments/<id>/cancel")
    print("- POST /appointments/<id>/reschedule")
    print("- GET /search")
    print("- GET /slots/suggest")
    print("- POST /appointments/<id>/send-reminder")    
    
    app.run(debug=True, host='0.0.0.0', port=5000)











