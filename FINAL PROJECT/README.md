# 🚗 Car Rental Service API (FastAPI)

This is a simple Car Rental backend project built using FastAPI.
It supports basic operations like adding cars, renting them, filtering, searching, sorting, and pagination.

---

## 📌 Features

- Add, update, delete cars
- Prevent duplicate entries
- Rent a car with cost calculation
- Business rule: cannot delete rented cars
- Filter cars by brand, type, availability
- Search cars (case-insensitive)
- Sort cars by any field
- Pagination support
- Combined endpoint (search + filter + sort + pagination)
- Rental search and pagination

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn

---

## ▶️ How to Run

1. Install dependencies:
    pip install -r requirements.txt

2. Run the server:   
    uvicorn main:app --reload

3. Open Swagger UI:
    http://127.0.0.1:8000/docs

---

## 📂 API Endpoints

### Car Operations
- POST /cars → Add car  
- GET /cars → Get all cars  
- GET /cars/{car_id} → Get single car  
- PUT /cars/{car_id} → Update car  
- DELETE /cars/{car_id} → Delete car  

### Advanced Car Features
- GET /cars/summary → Car summary  
- GET /cars/filter → Filter cars  
- GET /cars/search → Search cars  
- GET /cars/sort → Sort cars  
- GET /cars/page → Pagination  
- GET /cars/browse → Combined operations  

### Rental Operations
- POST /rentals → Create rental  
- GET /rentals → Get all rentals  
- GET /rentals/search → Search rentals  
- GET /rentals/page → Paginate rentals  

---

## 💰 Rental Cost Logic

- Base cost = price_per_day × days  
- 5% discount if days > 7  
- ₹50 insurance (optional)  
- 10% tax applied  
- Final total includes all charges  

---

## 🔄 Workflow Example

1. Add a car  
2. Rent the car  
3. Car becomes unavailable  
4. Cannot delete rented car  

---

## 🎯 Project Purpose

This project was built to understand:
- API development using FastAPI  
- Request validation using Pydantic  
- Real-world business logic implementation  
- CRUD operations and data handling  

---

## 👨‍💻 Author

Sanjay