# Digi-रक्षा Backend Setup Guide

## Prerequisites
1. Python 3.8 or higher
2. Supabase account and project
3. Virtual environment (recommended)

## Installation Steps

### 1. Create and activate virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Supabase Setup
1. Create a new project on [Supabase](https://supabase.com)
2. Go to Settings > API to get your project URL and anon key
3. Go to SQL Editor and run the SQL script from `database_setup.sql`

### 4. Environment Configuration
1. Copy `.env.example` to `.env`
2. Update the following values in `.env`:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   SECRET_KEY=your-secret-key-for-jwt
   ```

### 5. Generate Secret Key
Run this command to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Run the application
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation
Once running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### SOS Alerts
- `POST /api/sos/` - Create SOS alert
- `GET /api/sos/` - Get all SOS alerts
- `GET /api/sos/nearby` - Get nearby SOS alerts
- `POST /api/sos/safe` - Mark as safe

### Incidents
- `POST /api/incidents/` - Report incident
- `GET /api/incidents/` - Get all incidents
- `GET /api/incidents/{id}` - Get specific incident

### Missing Persons
- `POST /api/missing/` - Report missing person
- `GET /api/missing/` - Get all missing persons
- `GET /api/missing/{id}` - Get specific missing person

### Community
- `POST /api/community/` - Create community post
- `GET /api/community/` - Get all community posts
- `GET /api/community/{id}` - Get specific post

## Frontend Integration
To connect your frontend with this backend, you'll need to:

1. Update the frontend JavaScript to make API calls to `http://localhost:8000`
2. Handle authentication tokens in localStorage
3. Add error handling for API responses
4. Update form submissions to use the API endpoints

## Example Frontend Integration
```javascript
// Example login function
async function loginUser(govIdNumber, password) {
    try {
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                gov_id_number: govIdNumber,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            return data;
        } else {
            throw new Error('Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Example authenticated API call
async function createSOSAlert(latitude, longitude) {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch('http://localhost:8000/api/sos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude,
                location_description: 'Emergency location',
                emergency_type: 'General Emergency'
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error('Failed to create SOS alert');
        }
    } catch (error) {
        console.error('SOS alert error:', error);
        throw error;
    }
}
```

## Testing
You can test the API using:
1. The built-in FastAPI documentation at `/docs`
2. Postman or similar API testing tools
3. curl commands
4. Python requests library

## Production Deployment
For production deployment:
1. Set `DEBUG=False` in your environment
2. Use a production WSGI server like Gunicorn
3. Set up proper CORS origins instead of allowing all
4. Use environment variables for all sensitive configuration
5. Set up proper database connection pooling
6. Implement proper logging and monitoring

## Troubleshooting
1. **Import errors**: Make sure all dependencies are installed and virtual environment is activated
2. **Database connection errors**: Check your Supabase URL and key in `.env`
3. **CORS errors**: Make sure CORS is properly configured in `main.py`
4. **Authentication errors**: Ensure you're sending the Bearer token correctly