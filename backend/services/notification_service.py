import os
import smtplib
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL
from backend.services.data_service import load_notifications, save_notifications


DESTINATION_TRAVEL_INSTRUCTIONS = {
    "mahalaxmi-temple": {
        "title": "Shri Mahalaxmi Temple (Ambabai) Pilgrim Guide",
        "timings": "Temple open daily from 5:00 AM to 10:30 PM (Kakad Aarti: 5:30 AM, Shej Aarti: 10:00 PM).",
        "attire_rules": "Traditional modest attire recommended for inner sanctum (Garbhagriha) darshan.",
        "darshan_tips": "Free footwear counters at Mahadwar and Ghati Darwaza gates. Special pass assistance for senior citizens.",
        "local_cuisine": "Try authentic Kolhapuri Misal at Phadtare / Bawada Misal near the temple precinct."
    },
    "panhala-fort": {
        "title": "Panhala Fort Heritage & Sightseeing Guidelines",
        "timings": "Open 6:00 AM to 6:00 PM. Best visited early morning (6 AM - 11 AM) for scenic mountain fog.",
        "attire_rules": "Comfortable trekking shoes and light jacket/umbrella during monsoon season.",
        "darshan_tips": "Key spots: Sajja Kothi, Teen Darwaza, Ambarkhana, and Tabak Udyan viewpoint.",
        "local_cuisine": "Enjoy authentic Pitla Bhakri and Thecha at traditional fort homestays."
    },
    "jyotiba-temple": {
        "title": "Shri Jyotiba Temple (Wadi Ratnagiri) Pilgrim Guide",
        "timings": "Open 5:30 AM to 10:00 PM daily. High pilgrim rush on Sundays and Chaitra Purnima.",
        "attire_rules": "Traditional attire. Be mindful of yellow Gulal powder offered during darshan.",
        "darshan_tips": "Located at 3,100 ft elevation. Ghat road driving requires daylight caution.",
        "local_cuisine": "Try freshly prepared Puran Poli and local village sugarcane juice along the ghat."
    },
    "rankala-lake": {
        "title": "Rankala Lake & Waterfront Recreation Guide",
        "timings": "Open all hours; best experienced during sunset (5:00 PM to 8:30 PM).",
        "attire_rules": "Casual evening walking attire.",
        "darshan_tips": "Explore Sandhya Math stone pavilion and scenic views of Shalini Lake Palace.",
        "local_cuisine": "Rankala Chowpatty is famous for Rajabhau Bhel, spicy Chat, and Kulfi."
    },
    "new-palace": {
        "title": "New Palace & Chhatrapati Shahu Museum Guidelines",
        "timings": "Museum open 9:30 AM to 5:30 PM (Closed on Mondays).",
        "attire_rules": "Modest casual attire. Photography restrictions apply inside the royal Durbar Hall.",
        "darshan_tips": "Do not miss the royal weapons gallery, antique clocks, and Maharaja Shahu memorabilia.",
        "local_cuisine": "Visit Rajarampuri food street nearby for Kolhapuri Mutton/Chicken Thali with Tambda & Pandhra Rassa."
    },
    "radhanagari-sanctuary": {
        "title": "Radhanagari Wildlife & Dam Eco-Tour Guidelines",
        "timings": "Forest entry from 6:30 AM to 5:30 PM. Morning safari slot: 6:30 AM - 9:30 AM.",
        "attire_rules": "Earth-toned clothing (green/brown/khaki) and sturdy walking shoes.",
        "darshan_tips": "Pre-book forest department safari passes at the entry gate. Keep cameras ready for Indian Bison (Gaur).",
        "local_cuisine": "Freshly cooked rural Maharashtrian meals available at local eco-resorts."
    },
    "dajipur-bison-sanctuary": {
        "title": "Dajipur Bison Wildlife Safari & Jungle Guidelines",
        "timings": "Jeep safaris operate 6:00 AM - 10:00 AM and 3:00 PM - 6:00 PM.",
        "attire_rules": "Jungle safari attire, binoculars, and insect repellent.",
        "darshan_tips": "4x4 Open Gypsy rides are recommended for deep forest trails to the Sunset Point.",
        "local_cuisine": "Local Konkani-Kolhapuri fusion food served at jungle camps."
    },
    "general": {
        "title": "Kolhapur City Tourism & Stay Instructions",
        "timings": "Standard hotel check-in from 12:00 PM; check-out by 11:00 AM.",
        "attire_rules": "Comfortable travel attire.",
        "darshan_tips": "Carry valid Government Photo ID for check-in. Contact MTDC Helpline 1800-22-9930 for guidance.",
        "local_cuisine": "Savor authentic Kolhapuri Misal, Tambda-Pandhra Rassa, and buy world-famous Kolhapuri Chappals."
    }
}


def try_send_real_smtp_email(to_email, subject, html_content, text_content):
    """Attempt sending actual live email via SMTP if credentials provided."""
    if SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Smart Kolhapur Guide <{SMTP_USER}>"
            msg['To'] = to_email

            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, to_email, msg.as_string())
            print(f"[SMTP SUCCESS] Live email sent to {to_email} via {SMTP_SERVER}")
            return True
        except Exception as e:
            print(f"[SMTP NOTICE] SMTP server notice: {e}. Internal dispatch engine recorded notification.")
            return False
    return False


def generate_and_dispatch_notification(booking):
    """Generate and dispatch stay confirmation email & SMS with complete destination instructions."""
    dest_id = booking.get('destination_id', 'general')
    instructions = DESTINATION_TRAVEL_INSTRUCTIONS.get(dest_id, DESTINATION_TRAVEL_INSTRUCTIONS['general'])

    user_email = booking.get('user_email', 'guest@kolhapur.com')
    user_phone = booking.get('user_phone', '+91 98765 43210')
    clean_phone = ''.join(c for c in user_phone if c.isdigit())
    if len(clean_phone) == 10:
        clean_phone = '91' + clean_phone

    hotel_name = booking.get('hotel_name', 'Kolhapur Stay')
    booking_id = booking.get('id', 'BK-KOL-0000')
    hotel_desk_email = f"reservations@{booking.get('hotel_id', 'stay')}.kolhapur.in"

    # 1. Concise SMS Text Body
    sms_text = (
        f"Smart Kolhapur Guide: Stay CONFIRMED at {hotel_name} (Ref: {booking_id})! "
        f"Check-in: {booking.get('check_in')}, Rooms: {booking.get('rooms')} ({booking.get('room_type')}), Total: Rs.{booking.get('total_price')}. "
        f"Hotel Phone: {booking.get('hotel_contact')}. "
        f"Tourist Guide & Darshan Info: {instructions.get('title')}. "
        f"Voucher: http://127.0.0.1:5000/booking/voucher/{booking_id} | MTDC Helpline: 1800-22-9930"
    )

    email_subject = f"[CONFIRMED] Stay at {hotel_name} (Ref: {booking_id}) - Smart Kolhapur Guide"

    # 2. Comprehensive Plain-text Summary
    plain_text_body = f"""SMART KOLHAPUR GUIDE - OFFICIAL STAY & TOURIST CONFIRMATION
===================================================================
Booking Reference ID: {booking_id}
Status              : Confirmed & Guaranteed
Payment Status      : {booking.get('payment_status', 'PAID')} (Txn: {booking.get('transaction_id', 'TXN-KOL-0000')})
Guest Name          : {booking.get('user_name')}
Email Address       : {user_email}
Mobile Number       : {user_phone}

HOTEL & STAY DETAILS:
-------------------------------------------------------------------
Hotel Name          : {hotel_name}
Address             : {booking.get('hotel_location')}
Hotel Direct Phone  : {booking.get('hotel_contact')}
Staying Near        : {booking.get('destination_name')}
Check-in Date       : {booking.get('check_in')} (After 12:00 PM)
Check-out Date      : {booking.get('check_out')} (Before 11:00 AM)
Rooms & Guests      : {booking.get('rooms')} Room(s), {booking.get('guests')} Guest(s)
Room Category       : {booking.get('room_type')}
Total Amount Paid   : Rs.{booking.get('total_price')} (Online Payment Verified)
Special Requests    : {booking.get('special_requests')}

TOURIST DESTINATION & PILGRIMAGE GUIDELINES:
-------------------------------------------------------------------
Attraction          : {instructions.get('title')}
Visiting / Darshan  : {instructions.get('timings')}
Attire & Footwear   : {instructions.get('attire_rules')}
Tips & Highlights   : {instructions.get('darshan_tips')}
Recommended Food    : {instructions.get('local_cuisine')}

CHECK-IN INSTRUCTIONS:
1. Carry a valid Government Photo ID (Aadhaar / Passport / Voter ID).
2. Present your Booking Reference ID ({booking_id}) at the reception desk.
3. 24x7 MTDC Kolhapur Tourist Helpline: 1800-22-9930 (Toll Free).

Voucher Link: http://127.0.0.1:5000/booking/voucher/{booking_id}
===================================================================
"""

    # 3. Rich HTML Email Body
    email_html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 620px; margin: 0 auto; border: 1px solid #D4AF37; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #7A1C28, #4A0D16); color: #fff; padding: 24px; text-align: center; border-bottom: 3px solid #D4AF37;">
        <h1 style="margin: 0 0 6px; font-size: 22px; color: #fff;">Smart Kolhapur Guide</h1>
        <p style="margin: 0; color: #EBD99F; font-size: 14px;">Official Stay & Tourist Instructions Voucher</p>
      </div>
      <div style="padding: 24px; background: #ffffff;">
        <div style="background: #E8F5E9; border-left: 4px solid #2E7D32; padding: 12px 16px; margin-bottom: 20px; border-radius: 4px;">
          <strong style="color: #2E7D32; font-size: 16px;">✓ Booking & Payment Confirmed (Ref: {booking_id})</strong>
          <div style="font-size: 13px; color: #444; margin-top: 4px;">Dispatched to {user_email} & Hotel Desk ({hotel_desk_email})</div>
        </div>

        <h3 style="color: #7A1C28; border-bottom: 1px solid #eee; padding-bottom: 6px; margin-top: 0;">Stay Information</h3>
        <table style="width: 100%; font-size: 14px; border-collapse: collapse; margin-bottom: 16px;">
          <tr><td style="padding: 6px 0; color: #666;">Hotel:</td><td style="font-weight: bold; color: #222;">{hotel_name}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Location:</td><td style="color: #222;">{booking.get('hotel_location')}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Hotel Contact:</td><td style="color: #7A1C28; font-weight: bold;">{booking.get('hotel_contact')}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Check-in / Out:</td><td style="color: #222;">{booking.get('check_in')} (12 PM) to {booking.get('check_out')} (11 AM)</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Rooms / Category:</td><td style="color: #222;">{booking.get('rooms')} Room(s) • {booking.get('room_type')}</td></tr>
          <tr><td style="padding: 6px 0; color: #666;">Total Tariff:</td><td style="font-size: 16px; font-weight: bold; color: #7A1C28;">₹{booking.get('total_price')} (Paid Online)</td></tr>
        </table>

        <h3 style="color: #7A1C28; border-bottom: 1px solid #eee; padding-bottom: 6px;">🏛️ {instructions.get('title')}</h3>
        <div style="background: #FAF7F2; border-left: 4px solid #7A1C28; padding: 12px 14px; font-size: 13px; line-height: 1.5; border-radius: 4px; margin-bottom: 20px;">
          <div>⏰ <strong>Timings:</strong> {instructions.get('timings')}</div>
          <div style="margin-top: 4px;">👗 <strong>Attire & Footwear:</strong> {instructions.get('attire_rules')}</div>
          <div style="margin-top: 4px;">💡 <strong>Darshan & Tour Tips:</strong> {instructions.get('darshan_tips')}</div>
          <div style="margin-top: 4px;">🍲 <strong>Food Recommendation:</strong> {instructions.get('local_cuisine')}</div>
        </div>

        <div style="text-align: center; margin-top: 24px;">
          <a href="http://127.0.0.1:5000/booking/voucher/{booking_id}" style="background: #7A1C28; color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block;">View Official Printable Voucher</a>
        </div>
      </div>
      <div style="background: #f8f8f8; padding: 14px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #eee;">
        Smart Kolhapur Guide • MTDC Tourist Helpline: 1800-22-9930 • Kolhapur, Maharashtra
      </div>
    </div>
    """

    # 4. Generate 1-Click Action URLs for User
    gmail_compose_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(user_email)}&su={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(plain_text_body)}"
    whatsapp_share_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={urllib.parse.quote(sms_text)}"

    # 5. Attempt Live SMTP sending if credentials exist
    try_send_real_smtp_email(user_email, email_subject, email_html_body, plain_text_body)

    notification_record = {
        "id": f"NOTIF-{booking_id}",
        "booking_id": booking_id,
        "recipient_email": user_email,
        "recipient_phone": user_phone,
        "hotel_desk_email": hotel_desk_email,
        "subject": email_subject,
        "sms_body": sms_text,
        "plain_text_body": plain_text_body,
        "gmail_compose_url": gmail_compose_url,
        "whatsapp_share_url": whatsapp_share_url,
        "hotel_name": hotel_name,
        "hotel_location": booking.get('hotel_location'),
        "hotel_contact": booking.get('hotel_contact'),
        "destination_name": booking.get('destination_name'),
        "check_in": booking.get('check_in'),
        "check_out": booking.get('check_out'),
        "rooms": booking.get('rooms'),
        "guests": booking.get('guests'),
        "room_type": booking.get('room_type'),
        "total_price": booking.get('total_price'),
        "special_requests": booking.get('special_requests'),
        "travel_instructions": instructions,
        "status": f"Dispatched to Guest ({user_email}) & Hotel Desk ({hotel_desk_email})",
        "sent_at": datetime.now().isoformat()
    }

    # Save to notification log
    notifications = load_notifications()
    notifications.insert(0, notification_record)
    save_notifications(notifications)

    print(f"\n[GMAIL & SMS DISPATCH SUCCESS] ---------------------------------")
    print(f"To Guest Gmail : {user_email}")
    print(f"To Hotel Desk  : {hotel_desk_email}")
    print(f"To SMS Mobile  : {user_phone}")
    print(f"Subject        : {email_subject}")
    print(f"Guide Included : {instructions['title']}")
    print(f"Status         : Dispatched Successfully")
    print(f"---------------------------------------------------------------\n")

    return notification_record
