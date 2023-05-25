
# Auction
## Introduction
This is a simple auction system that allows users to participate in online auctions. It provides a platform where users can place bids on items and compete with other bidders to win the auction.

## How to run
To run the auction system, follow the steps below:

### 1. Initialize Redis
First, make sure you have Redis installed on your system. If not, you can use Docker to run a Redis container. Open your terminal and execute the following command to start a Redis container:
```sh
docker run -tid -p 6379:6379 redis
```
This command will start a Redis container in the background and map port 6379 of the container to port 6379 on your local machine.

### 2. Install Python Packages
Before running the auction server, you need to install the required Python packages. Make sure you have Python and pip installed. Open your terminal and navigate to the project directory. Then, execute the following command to install the necessary packages:
```sh
pip install -r requirements.txt
```
This command will install all the required packages specified in the `requirements.txt` file.

### 3. Run the Server
Once Redis is running and the Python packages are installed, you can start the auction server. In your terminal, navigate to the project directory and execute the following command:

```sh
python servidor.py
```
This command will start the auction server, and it will be ready to accept connections from clients.

### 4. Open Client HTML
To participate in the auction as a customer, open the `client.html` file in your web browser. Each time you open this file, a new customer will be created and connected to the auction server. You can open multiple instances of `client.html` to simulate multiple customers bidding on items.

## Usage
Once the server is running and clients are connected, you can start the auction process. The auction system provides an interface where customers can view the available items, place bids, and monitor the bidding activity in real-time. Customers can compete with each other by placing higher bids on items they are interested in. The highest bidder at the end of the auction wins the item.
