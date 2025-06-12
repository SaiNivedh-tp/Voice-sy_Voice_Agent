# Voice'sy


<img src="https://github.com/user-attachments/assets/94434750-09fa-41b0-882d-b7f2ecd12675" alt="Voice'sy Banner" width="500" height="500">


<br>
<br/>
<br/>


 Barbershops and dental clinics often rely on manual or web-based booking systems, resulting in lost appointments due to missed calls or delays in responses. These establishments usually use booking applications like Fresha, Calendly, or Zocdoc, which expose APIs for scheduling,rescheduling, and canceling appointments.


<br>

## Expected output

- Say or text: "I'd like a haircut tomorrow at 5 PM" or "Book a dental checkup next Friday."
- Interact with a voice bot over phone or smart devices.
  
### These AI agents will:
- Schedule appointments.
- Provide information about services and availability.
- Cancel or reschedule appointments.
- Send confirmations and reminders.
- Remember returning customers' preferences


## High level workflow


![image](https://github.com/user-attachments/assets/857769c6-1bbd-45f3-80da-55dc22bdcada)

![Untitled-2025-06-12-1011](https://github.com/user-attachments/assets/69334436-0433-4996-8ee0-6da2226b3d5d)



### Endpoints

```
    - POST /users/register"
    - POST /users/login"
    - GET /users/profile"
    - GET /providers"
    - GET /providers/<id>"
    - GET /services"
    - GET /providers/<id>/availability"
    - POST /appointments"
    - GET /appointments"
    - POST /appointments/<id>/cancel"
    - POST /appointments/<id>/reschedule"
    - GET /search"
    - GET /slots/suggest"
    - POST /appointments/<id>/send-reminder"
```
