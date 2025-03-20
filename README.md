# CarSharing Project

## Overview
This project implements a simplified CarSharing feature, involving multiple entities that communicate to facilitate the rental process.

## Entities
### 1. Phone Application (Client)
- Allows users to:
  - Create a client profile
  - Register in the company backend
  - Query available cars for rental in their proximity
  - Start rental for a selected car
  - End rental for the rented car

### 2. Company Backend (Server)
- Maintains an overview of:
  - All existing cars
  - Vehicle Identification Numbers (VIN)
  - Locations of cars
- Receives requests from the phone application and approves or denies them based on decision criteria

### 3. Car Telematics Module
- Informed of rental start requests to unlock the car
- Reports car state to the backend for rental approval
- Receives rental end requests to lock the car

Multiple users and cars can be present in the system, each user having their own phone application.

## Communication Protocol
Entities will communicate using a structured protocol, such as:
```
Client Identifier | Message Identifier | Payload
```
### Message Identifiers:
- **0** – Register client
- **1** – Query cars available for rental
- **2** – Start rental for a selected car
- **3** – End rental of a previously rented car
- **4** – Notification of successful request execution
- **5** – Notification of errors during request execution

## Use Cases
### 1. Client Login
- A user logs into the phone application and provides personal details.
- The system authorizes or denies rentals based on these details.

### 2. Query Available Cars
- The user (logged in) requests a list of nearby available rental cars.
- The request is processed between the phone application and the company backend.

### 3. Start Rental
- The user selects a car from the list and requests to start the rental.
- The request reaches the backend for approval.
- If approved:
  - The backend notifies the user via the phone app.
  - The car telematics module receives the command to unlock the car.
- If denied:
  - The backend informs the user via the phone app.

### 4. End Rental
- The user requests to end the rental for the selected car.
- The request is sent to the backend for approval.
- The backend checks the car's state (e.g., doors closed, lights off, etc.).
- If the car state is valid:
  - The backend approves the request.
  - The car receives the command to lock itself.
- If the state is invalid:
  - The backend sends an error message to the user.
  - The user must correct the issue and retry ending the rental.

## Tasks
### Exercise 1: Software Architecture
#### UML Diagrams
- **Class Diagram**: Defines system entities, roles, and message exchanges.
- **Sequence Diagram(s)**: Shows how entities communicate to accomplish use cases.

**Grading:**
- Class Diagram: **1 point**
- Sequence Diagram(s): **2 points**

### Exercise 2: Implementation
#### Client-Server Application
- The implementation follows the designed software architecture.

#### Demo Use Cases
| Use Case                | Points |
|-------------------------|--------|
| Client Login            | 0.5    |
| Query Available Cars    | 0.5    |
| Start Rental            | 1.0    |
| End Rental              | 1.0    |

**Use Case Dependencies:**
1. Login is required before querying available cars.
2. Query is needed before selecting and renting a car.
3. Rental must be active before requesting end rental.

