CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

CREATE TABLE IF NOT EXISTS menu (
  id INT AUTO_INCREMENT PRIMARY KEY,
  branch INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  portion VARCHAR(100),
  price INT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  branch INT NOT NULL,
  item_name VARCHAR(255) NOT NULL,
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Sample Menu Data for Branch 1
INSERT INTO menu (branch, name, category, portion, price) VALUES
(1, 'Margherita Pizza', 'Pizza', 'Medium', 500),
(1, 'Veggie Burger', 'Burger', 'Single', 350),
(1, 'Caesar Salad', 'Salad', 'Large', 400),
(1, 'Spicy Chicken Wings', 'Appetizer', '6 pcs', 450),
(1, 'Chocolate Brownie', 'Dessert', 'Piece', 200);

-- Sample Menu Data for Branch 2
INSERT INTO menu (branch, name, category, portion, price) VALUES
(2, 'Pepperoni Pizza', 'Pizza', 'Medium', 550),
(2, 'Cheese Burger', 'Burger', 'Single', 380),
(2, 'Greek Salad', 'Salad', 'Large', 420),
(2, 'Garlic Bread', 'Appetizer', '4 pcs', 250),
(2, 'Ice Cream Sundae', 'Dessert', 'Cup', 180);

-- Sample Orders for Branch 1
INSERT INTO orders (branch, item_name) VALUES
(1, 'Margherita Pizza'),
(1, 'Margherita Pizza'),
(1, 'Veggie Burger'),
(1, 'Caesar Salad'),
(1, 'Spicy Chicken Wings');
