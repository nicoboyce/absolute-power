-- Database schema for power tracker

-- Price history table
CREATE TABLE price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    retailer VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    in_stock BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url TEXT,
    
    INDEX idx_product_retailer (product_id, retailer),
    INDEX idx_scraped_at (scraped_at),
    INDEX idx_product_time (product_id, scraped_at)
);

-- Email subscriptions (for future use)
CREATE TABLE email_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    price_threshold DECIMAL(10,2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unsubscribe_token VARCHAR(64),
    
    UNIQUE KEY unique_email_product (email, product_id),
    INDEX idx_active (active),
    INDEX idx_product (product_id)
);

-- Scraping log table
CREATE TABLE scrape_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    retailer VARCHAR(50) NOT NULL,
    product_id VARCHAR(100),
    status ENUM('success', 'error', 'not_found') NOT NULL,
    error_message TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time INT, -- milliseconds
    
    INDEX idx_retailer_status (retailer, status),
    INDEX idx_scraped_at (scraped_at)
);

-- Views for easier querying

-- Latest prices per product per retailer
CREATE VIEW latest_prices AS
SELECT 
    product_id,
    retailer,
    price,
    currency,
    in_stock,
    scraped_at,
    url
FROM price_history p1
WHERE scraped_at = (
    SELECT MAX(scraped_at) 
    FROM price_history p2 
    WHERE p2.product_id = p1.product_id 
    AND p2.retailer = p1.retailer
);

-- Price comparison across retailers
CREATE VIEW price_comparison AS
SELECT 
    product_id,
    COUNT(*) as retailer_count,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    MAX(scraped_at) as last_updated
FROM latest_prices 
WHERE in_stock = TRUE
GROUP BY product_id;