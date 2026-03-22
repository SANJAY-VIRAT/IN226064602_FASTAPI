from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# simple in-memory storage (no database used here)
cars = []
rentals = []

# counters to generate ids
car_counter = 1
rental_counter = 1

# -------------------- MODELS --------------------

# input model for creating car
class CarCreate(BaseModel):
    model: str
    brand: str
    type: str
    price_per_day: float = Field(..., gt=0)

# full car model (includes id and availability)
class Car(CarCreate):
    id: int
    is_available: bool = True

# input model for rental request
class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int
    days: int = Field(..., gt=0)
    insurance: bool = False

# rental response model
class Rental(BaseModel):
    id: int
    customer_name: str
    car_id: int
    days: int
    insurance: bool
    base_cost: float
    discount: float
    tax: float
    total_cost: float
    status: str

# -------------------- HELPERS --------------------

# find car using id
def get_car(car_id: int):
    for c in cars:
        if c.id == car_id:
            return c
    return None

# calculate full rental cost
def calculate_rental_cost(price_per_day, days, insurance):
    base = price_per_day * days
    discount = 0

    # discount if rented for more than a week
    if days > 7:
        discount = base * 0.05

    # fixed insurance charge
    insurance_cost = 50 if insurance else 0

    # tax on final amount
    tax = (base - discount + insurance_cost) * 0.10
    total = base - discount + insurance_cost + tax
    return base, discount, tax, total

# filter helper
def filter_logic(data, **kwargs):
    result = data
    for key, value in kwargs.items():
        if value is not None:
            result = [item for item in result if getattr(item, key) == value]
    return result

# search helper (case insensitive)
def search_logic(data, keyword):
    keyword = keyword.lower()
    return [
        c for c in data
        if keyword in c.model.lower() or keyword in c.brand.lower()
    ]

# sort helper
def sort_logic(data, sort_by, order):
    reverse = order == "desc"
    return sorted(data, key=lambda x: getattr(x, sort_by), reverse=reverse)

# pagination helper
def paginate(data, page, limit):
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": len(data),
        "page": page,
        "total_pages": (len(data) + limit - 1) // limit,
        "data": data[start:end]
    }

# -------------------- ROUTES --------------------

@app.get("/")
def home():
    return {"message": "Welcome to SpeedRide Car Rentals!"}

# summary of cars
@app.get("/cars/summary")
def summary():
    available = len([c for c in cars if c.is_available])
    return {"total": len(cars), "available": available}

# filter cars
@app.get("/cars/filter")
def filter_cars(
    brand: Optional[str] = None,
    type: Optional[str] = None,
    is_available: Optional[bool] = None
):
    return filter_logic(cars, brand=brand, type=type, is_available=is_available)

# search cars
@app.get("/cars/search")
def search(keyword: str):
    result = search_logic(cars, keyword)
    if not result:
        return {"message": "No results found"}
    return result

# sort cars
@app.get("/cars/sort")
def sort(sort_by: str = "price_per_day", order: str = "asc"):
    return sort_logic(cars, sort_by, order)

# paginate cars
@app.get("/cars/page")
def pagination(page: int = 1, limit: int = 5):
    return paginate(cars, page, limit)

# combined endpoint (search + filter + sort + pagination)
@app.get("/cars/browse")
def browse(
    keyword: Optional[str] = None,
    brand: Optional[str] = None,
    type: Optional[str] = None,
    max_price: Optional[float] = None,
    is_available: Optional[bool] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = 1,
    limit: int = 5
):
    data = cars
    if keyword:
        data = search_logic(data, keyword)
    data = filter_logic(data, brand=brand, type=type, is_available=is_available)
    if max_price:
        data = [c for c in data if c.price_per_day <= max_price]
    data = sort_logic(data, sort_by, order)
    return paginate(data, page, limit)

# add new car
@app.post("/cars", status_code=201)
def add_car(car: CarCreate):
    global car_counter
    new_car = Car(id=car_counter, **car.dict())
    cars.append(new_car)
    car_counter += 1
    return new_car

# get all cars
@app.get("/cars")
def get_all_cars():
    return {"cars": cars, "total": len(cars)}

# prevent duplicate cars
@app.post("/cars/check", status_code=201)
def add_car_no_duplicate(car: CarCreate):
    for c in cars:
        if c.model == car.model and c.brand == car.brand:
            raise HTTPException(400, "Duplicate car")
    return add_car(car)

# create rental
@app.post("/rentals", status_code=201)
def create_rental(req: RentalRequest):
    global rental_counter
    car = get_car(req.car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    if not car.is_available:
        raise HTTPException(400, "Car not available")
    base, discount, tax, total = calculate_rental_cost(
        car.price_per_day, req.days, req.insurance
    )
    rental = Rental(
        id=rental_counter,
        customer_name=req.customer_name,
        car_id=req.car_id,
        days=req.days,
        insurance=req.insurance,
        base_cost=base,
        discount=discount,
        tax=tax,
        total_cost=total,
        status="active"
    )

    # mark car as rented
    car.is_available = False
    rentals.append(rental)
    rental_counter += 1
    return rental

# update car details
@app.put("/cars/{car_id}")
def update_car(car_id: int, updated: CarCreate):
    car = get_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    for key, value in updated.dict().items():
        setattr(car, key, value)
    return car

# delete car only if not rented
@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = get_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    if not car.is_available:
        raise HTTPException(400, "Car is rented")
    cars.remove(car)
    return {"message": "Deleted"}

# get all rentals
@app.get("/rentals")
def get_all_rentals():
    return rentals

# search rentals by customer name
@app.get("/rentals/search")
def search_rentals(customer_name: str):
    result = [
        r for r in rentals
        if customer_name.lower() in r.customer_name.lower()
    ]
    if not result:
        return {"message": "No rentals found"}
    return result

# paginate rentals
@app.get("/rentals/page")
def paginate_rentals(page: int = 1, limit: int = 5):
    return paginate(rentals, page, limit)

# get car by id (keep this at last to avoid conflicts)
@app.get("/cars/{car_id}")
def get_single_car(car_id: int):
    car = get_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return car
