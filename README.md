# E-Commerce Application

## 1. Functional Requirements

* Users can register and log in.
* Users can search and view products, including descriptions, prices, and other details.
* Users can add, remove, and update products in their shopping cart.
* Users can place orders using the items in their cart.
* Users can view their search history and order history.
* Admins can add, remove, and deactivate products.
* Admins can manage product inventory and stock availability.

## 2. Non-Functional Requirements

* **Availability:** Target 99.5% uptime.
* **API Latency:** 95% of normal API requests should complete within 300 ms (p95 latency).
* **Scalability:** Support multiple backend instances to handle increasing traffic.
* **Consistency:** Prevent overselling by ensuring that stock availability is handled correctly during concurrent purchases.
* **Reliability:** Retrying a checkout request must not create duplicate orders.
* **Security:** Implement password hashing, authentication, and input validation.
* **Observability:** Track request latency, error rates, and throughput.
* **Cost:** Develop and test the application locally for free, with a publicly accessible demo if possible.

## 3. Capacity Estimation

### 3.1 Assumptions

Having 10,000 registered users does not mean all 10,000 users are using the application simultaneously.

For this learning project, we will use the following assumptions:

| Metric                           |        Assumption |
| -------------------------------- | ----------------: |
| Registered users                 |            10,000 |
| Daily active users (DAU)         |             2,000 |
| Requests per active user per day |                50 |
| Total daily requests             |           100,000 |
| Average request rate             | ~1.2 requests/sec |
| Peak traffic (10× average)       |  ~12 requests/sec |
| Product catalogue                |    5,000 products |
| Average product record size      |              2 KB |

### 3.2 Calculating Requests Per Second (RPS)

**Step 1: Calculate total daily requests**

Assuming each daily active user makes 50 requests per day:

```text
Daily Requests = Daily Active Users × Requests per User

               = 2,000 × 50

               = 100,000 requests/day
```

**Step 2: Calculate average requests per second**

There are 86,400 seconds in a day.

```text
Average RPS = Total Daily Requests / Seconds per Day

            = 100,000 / 86,400

            ≈ 1.16 requests/second
```

Therefore, the average request rate is approximately **1.2 requests per second**.

**Step 3: Estimate peak traffic**

Traffic is not evenly distributed throughout the day. During peak periods, the application may receive significantly more requests than average.

Assuming peak traffic is 10 times the average:

```text
Peak RPS = Average RPS × Peak Traffic Multiplier

         = 1.16 × 10

         ≈ 11.6 requests/second
```

Therefore, the estimated peak traffic is approximately **12 requests per second**.

## 4. High Level System Architecture

<img width="662" height="1142" alt="Untitled Diagram drawio (1)" src="https://github.com/user-attachments/assets/2718f2ae-ddf0-4ac2-b2be-fb6c8540429e" />

