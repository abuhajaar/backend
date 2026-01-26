
import io from 'socket.io-client';

// Get JWT token from storage
const token = localStorage.getItem('jwt_token');

// Connect to announcements namespace
const announcementSocket = io('http://localhost:5001/announcements');

// Handle connection
announcementSocket.on('connect', () => {
  console.log('Connected to announcements WebSocket');
  
  // Authenticate with JWT token
  announcementSocket.emit('authenticate', { token });
});

// Handle authentication response
announcementSocket.on('authenticated', (data) => {
  console.log('Authenticated to announcements channel:', data);
  // data = { message, user_id, role, subscribed_to }
});

// Listen for new announcements
announcementSocket.on('created', (announcement) => {
  console.log('New announcement created:', announcement);
  
  // Add to your state/list
  setAnnouncements(prev => [announcement, ...prev]);
  
  // Show notification
  showNotification('New announcement: ' + announcement.title);
});

// Listen for updated announcements
announcementSocket.on('updated', (announcement) => {
  console.log('Announcement updated:', announcement);
  
  // Update in your state/list
  setAnnouncements(prev =>
    prev.map(a => a.id === announcement.id ? announcement : a)
  );
});

// Listen for deleted announcements
announcementSocket.on('deleted', (data) => {
  console.log('Announcement deleted:', data.id);
  
  // Remove from your state/list
  setAnnouncements(prev =>
    prev.filter(a => a.id !== data.id)
  );
});

// Handle errors
announcementSocket.on('error', (error) => {
  console.error('WebSocket error:', error.message);
});

// Disconnect when component unmounts
announcementSocket.on('disconnect', () => {
  console.log('Disconnected from announcements WebSocket');
});

// Clean up
const cleanup = () => {
  announcementSocket.disconnect();
};
