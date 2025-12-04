# Restaurant Recommendation Backend

This backend is built with **FastAPI** and **MySQL**. It provides a simple API that returns food recommendations based on menu data stored in the database.

---

## 1. Install MySQL

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install mysql-server
sudo service mysql start
```

### Mac with Homebrew
```bash
brew install mysql
brew services start mysql
```

---

## 2. Create MySQL User and Password
```bash
mysql -u root -p
```
```sql
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'strongpassword123';
GRANT ALL PRIVILEGES ON *.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

---

## 3. Create Database and Tables
```sql
CREATE DATABASE restaurant_db;
USE restaurant_db;

CREATE TABLE menu (
  id INT AUTO_INCREMENT PRIMARY KEY,
  branch INT NOT NULL,
  name VARCHAR(255),
  category VARCHAR(100),
  portion VARCHAR(100),
  price INT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  branch INT NOT NULL,
  item_name VARCHAR(255),
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO menu (branch, name, category, portion, price) VALUES
(1, 'Margherita Pizza', 'Pizza', 'Medium', 500),
(1, 'Veggie Burger', 'Burger', 'Single', 350),
(1, 'Caesar Salad', 'Salad', 'Large', 400),
(1, 'Spicy Chicken Wings', 'Appetizer', '6 pcs', 450),
(1, 'Chocolate Brownie', 'Dessert', 'Piece', 200);
```

---

## 4. Create Conda Environment
```bash
conda create -n fastapi_env python=3.12
conda activate fastapi_env
```

---

## 5. Install Dependencies

Create `requirements.txt`:
```txt
fastapi
uvicorn
python-dotenv
aiomysql
redis
pydantic
```

Install:
```bash
pip install -r requirements.txt
```

---

## 6. Create .env File
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=appuser
MYSQL_PASSWORD=strongpassword123
MYSQL_DB=restaurant_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=300
```

---

## 7. (Optional) Install Redis

### Ubuntu/Debian
```bash
sudo apt install redis-server
sudo service redis-server start
redis-cli ping  # Should return PONG
```

---

## 8. Run FastAPI Backend
```bash
uvicorn main:app --reload --port 8001
```

**Backend URL:** `http://localhost:8001`  
**Health Check:** `http://localhost:8001/health`

---

## 9. Test API
```bash
curl -X POST http://localhost:8001/api/recommend \
-H "Content-Type: application/json" \
-d '{
  "branch": 1,
  "question": {
    "peoples": 2,
    "mood": "happy",
    "spice_lvl": "medium",
    "avoid_anything": "nuts",
    "budget": "medium"
  }
}'
```

---

## 10. Frontend Integration

**Endpoint:** `POST http://localhost:8001/api/recommend`

**Request Body:**
```json
{
  "branch": 1,
  "question": {
    "peoples": 2,
    "mood": "happy",
    "spice_lvl": "medium",
    "avoid_anything": "nuts",
    "budget": "medium"
  }
}
```