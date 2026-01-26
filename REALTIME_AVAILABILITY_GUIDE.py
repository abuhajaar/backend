"""
WebSocket Real-time Space Availability Test

This demonstrates how space availability changes in real-time when bookings are created/cancelled.
"""

# Frontend Implementation Example
"""
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

const SpaceBooking = () => {
  const [spaces, setSpaces] = useState([]);
  const [selectedDate, setSelectedDate] = useState('2025-12-26');
  const [selectedTime, setSelectedTime] = useState({ start: '10:00', end: '15:00' });
  
  const token = localStorage.getItem('access_token');
  
  useEffect(() => {
    const socket = io('http://192.168.1.101:5000/spaces');
    
    // ========== CONNECTION & AUTHENTICATION ==========
    socket.on('connect', () => {
      console.log('✅ Connected to /spaces');
      socket.emit('authenticate', { token });
    });
    
    socket.on('authenticated', (data) => {
      console.log('✅ Authenticated:', data);
      // Fetch initial spaces data
      fetchSpaces();
    });
    
    // ========== INITIAL DATA LOAD ==========
    socket.on('spaces_data', (data) => {
      console.log(`📦 Received ${data.count} spaces`);
      console.log('Filters applied:', data.filters);
      setSpaces(data.spaces);
    });
    
    // ========== REAL-TIME EVENTS ==========
    
    // When admin changes space status (available ↔ maintenance)
    socket.on('updated', (space) => {
      console.log('🔧 Space status updated:', space);
      setSpaces(prev => 
        prev.map(s => s.id === space.id ? space : s)
      );
      showNotification(`Space "${space.name}" is now ${space.status}`);
    });
    
    // ⭐ NEW: When someone books/cancels - availability changed
    socket.on('availability_changed', (data) => {
      console.log('📅 Availability changed!');
      console.log(`  Space ID: ${data.space_id}`);
      console.log(`  Date: ${data.date}`);
      console.log(`  Time: ${data.affected_time_range.start} - ${data.affected_time_range.end}`);
      console.log(`  Message: ${data.message}`);
      
      // Re-fetch spaces to get updated availability
      fetchSpaces();
      
      showNotification('Space availability updated!');
    });
    
    // When admin creates new space
    socket.on('created', (space) => {
      console.log('🆕 New space created:', space);
      setSpaces(prev => [...prev, space]);
      showNotification(`New space "${space.name}" added`);
    });
    
    // When admin deletes space
    socket.on('deleted', (data) => {
      console.log('🗑️ Space deleted:', data.id);
      setSpaces(prev => prev.filter(s => s.id !== data.id));
      showNotification('Space removed');
    });
    
    socket.on('error', (data) => {
      console.error('❌ Error:', data.message);
    });
    
    // ========== HELPER FUNCTIONS ==========
    const fetchSpaces = () => {
      socket.emit('get_spaces', {
        date: selectedDate,
        start_time: selectedTime.start,
        end_time: selectedTime.end
      });
    };
    
    const showNotification = (message) => {
      // Your notification logic here
      alert(message);
    };
    
    return () => socket.disconnect();
  }, [token]);
  
  // ========== RENDER ==========
  return (
    <div>
      <h1>Book a Space</h1>
      
      {/* Date & Time Filters */}
      <div className="filters">
        <input 
          type="date" 
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
        <input 
          type="time" 
          value={selectedTime.start}
          onChange={(e) => setSelectedTime({...selectedTime, start: e.target.value})}
        />
        <input 
          type="time" 
          value={selectedTime.end}
          onChange={(e) => setSelectedTime({...selectedTime, end: e.target.value})}
        />
      </div>
      
      {/* Space List */}
      <div className="space-grid">
        {spaces.map(space => (
          <div 
            key={space.id}
            className={`space-card ${space.is_available ? 'available' : 'unavailable'}`}
          >
            <h3>{space.name}</h3>
            <p>{space.type} | Capacity: {space.capacity}</p>
            <p>Location: {space.location}</p>
            
            {/* Availability Status */}
            {space.is_available ? (
              <div className="available">
                <span className="badge green">✓ Available</span>
                {space.available_hours && space.available_hours.length > 0 && (
                  <div className="time-slots">
                    <strong>Available hours:</strong>
                    {space.available_hours.map((slot, i) => (
                      <span key={i} className="time-slot">
                        {slot.start} - {slot.end}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="unavailable">
                <span className="badge red">✗ Unavailable</span>
                {space.unavailable_reason && (
                  <p className="reason">{space.unavailable_reason}</p>
                )}
              </div>
            )}
            
            {/* Amenities */}
            <div className="amenities">
              {space.amenities.map(amenity => (
                <span key={amenity.id} className="amenity">
                  {amenity.icon} {amenity.name}
                </span>
              ))}
            </div>
            
            {/* Book Button */}
            {space.is_available && (
              <button 
                onClick={() => bookSpace(space.id)}
                className="btn-book"
              >
                Book Now
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SpaceBooking;
"""

# ================================================================================
# REAL-TIME FLOW SCENARIOS
# ================================================================================

"""
SCENARIO 1: User A books a space
================================
1. User A clicks "Book Now" on Space #1
   → POST /api/bookings
   {
     "space_id": 1,
     "user_id": 3,
     "start_at": "2025-12-26T10:00:00",
     "end_at": "2025-12-26T12:00:00"
   }

2. Backend:
   ✓ Creates booking in database
   ✓ Broadcasts to /bookings namespace:
     Event: "created"
     Data: { id: 123, space_id: 1, user_id: 3, ... }
   
   ✓ Broadcasts to /spaces namespace:
     Event: "availability_changed"
     Data: {
       space_id: 1,
       date: "2025-12-26",
       affected_time_range: { start: "10:00", end: "12:00" },
       message: "Space availability has changed"
     }

3. User B (viewing spaces list):
   → Receives "availability_changed" event
   → Automatically re-fetches spaces via WebSocket
   → Sees Space #1 now shows:
     - available_hours: [{ start: "08:00", end: "10:00" }, { start: "12:00", end: "18:00" }]
     - is_available: true (still available for other time slots)
   → OR if fully booked for requested time:
     - is_available: false
     - unavailable_reason: "This space is already booked by user_a from 10:00 to 12:00"

4. User C (viewing bookings list):
   → Receives "created" event on /bookings namespace
   → Sees new booking appear in real-time


SCENARIO 2: User A cancels booking
===================================
1. User A clicks "Cancel Booking"
   → PUT /api/bookings/123
   { "status": "cancel" }

2. Backend:
   ✓ Updates booking status to "cancelled"
   ✓ Broadcasts to /bookings namespace:
     Event: "updated"
     Data: { id: 123, status: "cancelled", ... }
   
   ✓ Broadcasts to /spaces namespace:
     Event: "availability_changed"
     Data: {
       space_id: 1,
       date: "2025-12-26",
       affected_time_range: { start: "10:00", end: "12:00" },
       message: "Space availability has changed"
     }

3. User B (viewing spaces):
   → Receives "availability_changed" event
   → Re-fetches spaces
   → Sees Space #1 is now available again:
     - available_hours: [{ start: "08:00", end: "18:00" }]
     - is_available: true


SCENARIO 3: Admin changes space status
=======================================
1. Admin sets Space #1 to maintenance
   → PUT /api/spaces/admin/1
   { "status": "maintenance" }

2. Backend:
   ✓ Updates space status in database
   ✓ Broadcasts to /spaces namespace:
     Event: "updated"
     Data: { id: 1, name: "Hot Desk 1.1", status: "maintenance", ... }

3. All users viewing spaces:
   → Receive "updated" event
   → Update Space #1 in UI immediately (no re-fetch needed)
   → See status badge change: "Available" → "Under Maintenance"
   → Book button disappears


SCENARIO 4: User A checks out early
====================================
1. User A clicks "Check Out" (before end time)
   → PUT /api/bookings/123
   { "status": "checkout" }

2. Backend:
   ✓ Updates booking status to "finished"
   ✓ Broadcasts to /bookings: "updated"
   ✓ Broadcasts to /spaces: "availability_changed"

3. Other users:
   → Space becomes available earlier than expected
   → Can now book the remaining time slot
"""

# ================================================================================
# BACKEND EVENTS SUMMARY
# ================================================================================

"""
WEBSOCKET EVENTS EMITTED BY BACKEND

/spaces namespace:
------------------
1. spaces_data - Initial data or re-fetch response
   Triggered by: Client emits "get_spaces"
   Data: { spaces: [...], count: 35, filters: {...} }

2. updated - Space status changed (admin action)
   Triggered by: PUT /api/spaces/admin/:id
   Data: { id, name, status, ... } (full space object)

3. created - New space added (admin action)
   Triggered by: POST /api/spaces/admin
   Data: { id, name, type, ... } (full space object)

4. deleted - Space removed (admin action)
   Triggered by: DELETE /api/spaces/admin/:id
   Data: { id: 5 }

5. availability_changed - Booking created/cancelled ⭐ NEW
   Triggered by: POST /api/bookings, PUT /api/bookings/:id (cancel/checkout)
   Data: {
     space_id: 1,
     date: "2025-12-26",
     affected_time_range: { start: "10:00", end: "12:00" },
     message: "Space availability has changed"
   }

/bookings namespace:
--------------------
1. bookings_data - Initial data
2. created - New booking created
3. updated - Booking status changed (checkin/checkout/cancel)
4. deleted - Booking deleted
"""

# ================================================================================
# TESTING
# ================================================================================

"""
TO TEST THE REAL-TIME FUNCTIONALITY:

1. Open 2 browser windows side-by-side

WINDOW 1 (User A - Employee):
- Login as employee
- Navigate to spaces page
- Set date/time filters: 2025-12-26, 10:00-15:00
- See list of available spaces

WINDOW 2 (User B - Employee):
- Login as different employee
- Navigate to same spaces page
- Same filters: 2025-12-26, 10:00-15:00
- See same list of spaces

ACTION:
Window 1: Book Space #1 from 10:00-12:00

EXPECTED RESULT:
Window 2 AUTOMATICALLY updates:
- Space #1 available_hours changes
- If time 10:00-15:00 includes 10:00-12:00, space shows partially available
- No page refresh needed!

CONSOLE LOGS in Window 2:
📅 Availability changed!
  Space ID: 1
  Date: 2025-12-26
  Time: 10:00 - 12:00
  Message: Space availability has changed
📦 Received 35 spaces (after re-fetch)
"""
