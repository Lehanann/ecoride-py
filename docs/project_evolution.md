# Project Evolution

## 1. Initial Features
The project started with the implementation of core features:
- User
- Carpooling
- Reservation
- Opinion

At this stage, the focus was on functionality rather than structure.

---

## 2. Authentication Middleware
A minimal authentication middleware was introduced:
- Extract user_id from request
- Attach it to request.state

This allowed the backend to control user identity securely.

---

## 3. Refactor Phase
A global refactor was performed to improve:
- Code structure (Repository / Service separation)
- Naming consistency
- Reduction of duplicated logic

---

## 4. Exception Handling
Custom exception handling was introduced:
- Centralized HTTP errors
- Consistent error messages
- Improved debugging and API reliability

---

## 5. Testing
Unit tests were added to ensure:
- Business logic correctness
- Edge cases handling
- Regression prevention

---

## Future Improvements
- International phone support
- Prevent duplicate transaction generation
- Improve role management flexibility