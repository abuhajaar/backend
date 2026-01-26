"""
WebSocket Test Script
Run this in your browser console or use it as a reference for frontend implementation
"""

# Install socket.io-client first: npm install socket.io-client

# JavaScript/TypeScript Example
"""
import io from 'socket.io-client';

const token = 'YOUR_JWT_TOKEN_HERE';
const baseURL = 'http://192.168.1.101:5000';

// ==================== ANNOUNCEMENTS ====================
console.log('Testing /announcements namespace...');
const announcementSocket = io(`${baseURL}/announcements`, {
  transports: ['websocket', 'polling'],
  reconnection: true
});

announcementSocket.on('connect', () => {
  console.log('✅ Connected to /announcements');
  announcementSocket.emit('authenticate', { token });
});

announcementSocket.on('connection_response', (data) => {
  console.log('Connection response:', data);
});

announcementSocket.on('authenticated', (data) => {
  console.log('✅ Authenticated to announcements:', data);
});

announcementSocket.on('announcements_initial', (data) => {
  console.log('📦 Initial announcements:', data);
});

announcementSocket.on('created', (data) => {
  console.log('📢 New announcement:', data);
});

announcementSocket.on('updated', (data) => {
  console.log('✏️ Announcement updated:', data);
});

announcementSocket.on('deleted', (data) => {
  console.log('🗑️ Announcement deleted:', data);
});

announcementSocket.on('error', (data) => {
  console.error('❌ Announcement error:', data);
});

// ==================== SPACES ====================
console.log('Testing /spaces namespace...');
const spaceSocket = io(`${baseURL}/spaces`, {
  transports: ['websocket', 'polling'],
  reconnection: true
});

spaceSocket.on('connect', () => {
  console.log('✅ Connected to /spaces');
  spaceSocket.emit('authenticate', { token });
});

spaceSocket.on('authenticated', (data) => {
  console.log('✅ Authenticated to spaces:', data);
  
  // Fetch spaces with optional filters
  spaceSocket.emit('get_spaces', {
    date: '2026-01-26',      // optional
    start_time: '09:00',     // optional
    end_time: '17:00'        // optional
  });
});

spaceSocket.on('spaces_data', (data) => {
  console.log('📦 Spaces data:', data);
});

spaceSocket.on('created', (data) => {
  console.log('🏢 New space:', data);
});

spaceSocket.on('updated', (data) => {
  console.log('✏️ Space updated:', data);
});

spaceSocket.on('deleted', (data) => {
  console.log('🗑️ Space deleted:', data);
});

// ==================== BOOKINGS ====================
console.log('Testing /bookings namespace...');
const bookingSocket = io(`${baseURL}/bookings`, {
  transports: ['websocket', 'polling'],
  reconnection: true
});

bookingSocket.on('connect', () => {
  console.log('✅ Connected to /bookings');
  bookingSocket.emit('authenticate', { token });
});

bookingSocket.on('authenticated', (data) => {
  console.log('✅ Authenticated to bookings:', data);
  
  // Fetch bookings (employees see their own, managers see department)
  bookingSocket.emit('get_bookings', { token });
});

bookingSocket.on('bookings_data', (data) => {
  console.log('📦 Bookings data:', data);
});

bookingSocket.on('created', (data) => {
  console.log('📅 New booking:', data);
});

bookingSocket.on('updated', (data) => {
  console.log('✏️ Booking updated:', data);
});

bookingSocket.on('deleted', (data) => {
  console.log('🗑️ Booking deleted:', data);
});

// ==================== STATUS CHECK ====================
setInterval(() => {
  console.log('Connection Status:');
  console.log('  Announcements:', announcementSocket.connected ? '🟢' : '🔴');
  console.log('  Spaces:', spaceSocket.connected ? '🟢' : '🔴');
  console.log('  Bookings:', bookingSocket.connected ? '🟢' : '🔴');
}, 5000);
"""

# Python Test Script (using python-socketio client)
"""
pip install "python-socketio[client]"

import socketio
import time

token = 'YOUR_JWT_TOKEN_HERE'
base_url = 'http://192.168.1.101:5000'

# Test Announcements
sio_announcements = socketio.Client()

@sio_announcements.on('connect', namespace='/announcements')
def on_connect():
    print('✅ Connected to /announcements')
    sio_announcements.emit('authenticate', {'token': token}, namespace='/announcements')

@sio_announcements.on('authenticated', namespace='/announcements')
def on_authenticated(data):
    print('✅ Authenticated:', data)

@sio_announcements.on('announcements_initial', namespace='/announcements')
def on_initial(data):
    print('📦 Initial announcements:', data)

@sio_announcements.on('created', namespace='/announcements')
def on_created(data):
    print('📢 New announcement:', data)

try:
    sio_announcements.connect(base_url, namespaces=['/announcements'])
    time.sleep(30)  # Keep connection alive for 30 seconds
except Exception as e:
    print(f'Error: {e}')
finally:
    sio_announcements.disconnect()
"""

# Browser Console Test (Vanilla JS)
"""
// Load Socket.IO client from CDN
const script = document.createElement('script');
script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js';
document.head.appendChild(script);

// Wait for script to load
setTimeout(() => {
  const token = 'YOUR_JWT_TOKEN_HERE';
  
  // Test Announcements
  const socket = io('http://192.168.1.101:5000/announcements');
  
  socket.on('connect', () => {
    console.log('✅ Connected');
    socket.emit('authenticate', { token: token });
  });
  
  socket.on('authenticated', (data) => {
    console.log('✅ Authenticated:', data);
  });
  
  socket.on('announcements_initial', (data) => {
    console.log('📦 Received:', data);
  });
  
  socket.on('error', (data) => {
    console.error('❌ Error:', data);
  });
}, 1000);
"""
