USE ecommerce;

SELECT * FROM orders;

-- Total Orders
SELECT COUNT(*) AS Total_orders
FROM orders;

-- Total Sales
SELECT SUM(Net_Amount) AS Total_Sales
FROM orders; 

-- Top Product
SELECT 
product,SUM(Net_Amount) as Sales
FROM orders
GROUP BY product
ORDER BY Sales DESC;
 
 
-- Top Cities 
SELECT 
city,SUM(Net_Amount) as Sales
FROM orders
GROUP BY city
ORDER BY Sales DESC;

-- Monthly Sales
SELECT 
month,SUM(Net_Amount) as Sales
FROM orders
GROUP BY month
ORDER BY Sales DESC;

-- Highest profit product
SELECT 
product,SUM(profit) as profit
FROM orders
GROUP BY product
ORDER BY profit DESC;

-- Payment mode distribution
SELECT 
payment_mode,
COUNT(*) as Total_orders
FROM orders
GROUP BY payment_mode;

-- cancelled orders
SELECT *
FROM orders
WHERE order_status;
 