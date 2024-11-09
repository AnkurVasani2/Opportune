# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


# def send_email(recommendation):
#     json_data = recommendation
#     print(json_data)
#     # Create a MIME message
#     msg = MIMEMultipart()
#     msg['From'] = 'ankurvasani2585@gmail.com'
#     msg['To'] = 'chintan222005@gmail.com'
#     msg['Subject'] = 'Exciting Course Recommendations Just for You!'

#     # Add body to the message
#     body = f'''
#     <html>
#     <body>
#     <p>Hi there,</p>

#     <p>We have handpicked a few exciting courses to help you level up your skills and explore new opportunities. Whether you’re looking to dive deeper into marketing analytics, electronics, or cybersecurity, these courses will guide you to success!</p>

#     <hr>

#     <p><b>1. {json_data["recommended_courses"][0]["course_name"]}</b> ({json_data["recommended_courses"][0]["level"]})<br>
#     <i>{json_data["recommended_courses"][0]["about"]}</i><br>
#     <a href="{json_data["recommended_courses"][0]["link"]}">Start Learning Now</a></p>

#     <hr>

#     <p><b>2. {json_data["recommended_courses"][1]["course_name"]}</b> ({json_data["recommended_courses"][1]["level"]})<br>
#     <i>{json_data["recommended_courses"][1]["about"]}</i><br>
#     <a href="{json_data["recommended_courses"][1]["link"]}">Start Learning Now</a></p>

#     <hr>

#     <p><b>3. {json_data["recommended_courses"][2]["course_name"]}</b> ({json_data["recommended_courses"][2]["level"]})<br>
#     <i>{json_data["recommended_courses"][2]["about"]}</i><br>
#     <a href="{json_data["recommended_courses"][2]["link"]}">Start Learning Now</a></p>

#     <hr>

#     <p>Each course has been designed to offer practical knowledge and real-world insights. Don’t miss out on the opportunity to advance your expertise and unlock new possibilities!</p>

#     <p>Happy Learning,<br>Team Opportune</p>
#     </body>
#     </html>
#     '''

#     msg.attach(MIMEText(body, 'html'))

#     # Send the email using Gmail's SMTP server
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()

#     # Replace 'your_password' with your actual app password (not your Gmail password)
#     server.login('ankurvasani2585@gmail.com', 'mmwk gxbf otkm hcjf')
    
#     # Send the email
#     text = msg.as_string()
#     server.sendmail(msg['From'], msg['To'], text)
    
#     # Close the connection
#     server.quit()

#     print("Email sent successfully!")
#     return True




# """import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import random

# def generate_otp():
#     return random.randint(100000, 999999)
# def send_email(receiver_email):
#     otp = generate_otp()
#     sender_email = 'chintan222005@gmail.com'
#     sender_password = 'iwuz nuqp szcw dtfr'
#     subject = 'Test Email'
#     message = f'This is a test email sent from Python. \n Your Otp is {otp}'
#     smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
#     smtp_server.starttls()
#     smtp_server.login(sender_email, sender_password)
#     email_message = MIMEMultipart()
#     email_message['From'] = sender_email
#     email_message['To'] = receiver_email
#     email_message['Subject'] = subject
#     email_message.attach(MIMEText(message, 'plain'))
#     smtp_server.send_message(email_message)
#     smtp_server.quit()
#     return otp
# """

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

def send_email():
    # Define the JSON object you want to send
    json_body = {
        "name": "John Doe",
        "email": "chintan222005@gmail.com",
        "message": "This is a test email containing JSON data.",
        "status": "success"
    }

    # Convert the JSON object to a string
    json_str = json.dumps(json_body, indent=4)

    # Email details
    sender_email = 'ankurvasani2585@gmail.com'
    sender_password = 'mmwk gxbf otkm hcjf'  # Make sure to store this securely
    subject = 'Test Email with JSON Body'
    message = f'Here is the JSON data:\n\n{json_str}'

    # Setting up SMTP server
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(sender_email, sender_password)

    # Create the email message
    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = "chintan222005@gmail.com"
    email_message['Subject'] = subject

    # Attach the JSON string as the email body
    email_message.attach(MIMEText(message, 'plain'))

    # Send the email
    smtp_server.send_message(email_message)
    smtp_server.quit()

    print(f"Email sent to ")
