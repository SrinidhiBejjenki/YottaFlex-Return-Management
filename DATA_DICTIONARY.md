# ReturnFlow – Data Dictionary

## 1. Overview

This document describes the database entities, fields, relationships and purpose of the ReturnFlow system.

All dataset records are synthetically generated.

## 2. Database Entities

### Customer
Stores customer information.
- customer_id: Unique customer identifier.
- name: Customer name.
- email: Unique email address.
- phone: Contact number.

### Order
Stores customer purchase information.
- order_id: Unique order identifier.
- customer_id: Reference to Customer.
- order_date: Purchase date.
- total_amount: Total order value.
- status: Order status.

### OrderLine
Stores individual products in an order.
- order: Reference to Order.
- product_name: Product name.
- quantity: Purchased quantity.
- unit_price: Price per unit.

### ReturnRequest
Stores customer return requests.
- return_id: Unique return identifier.
- order: Reference to Order.
- request_date: Return request date.
- reason: Return reason.
- status: Return status.

### ReturnLine
Stores products and quantities included in a return.
- return_request: Reference to ReturnRequest.
- order_line: Reference to OrderLine.
- quantity: Requested return quantity.

### ReturnAuthorization
Stores return approval information.
- authorization_id: Unique authorization identifier.
- return_request: Reference to ReturnRequest.
- approved: Approval decision.
- authorized_date: Authorization date.
- status: Authorization status.

### ReturnShipment
Tracks returned product shipments.
- shipment_id: Unique shipment identifier.
- authorization: Reference to ReturnAuthorization.
- tracking_number: Shipment tracking number.
- shipped_date: Shipment date.
- received_date: Received date.
- status: Shipment status.

### Inspection
Stores returned product inspection details.
- return_line: Reference to ReturnLine.
- inspected_date: Inspection date.
- condition: Product condition.
- notes: Inspection observations.
- inspected_by: Inspector information.

### Refund
Stores refund transactions and attempts.
- refund_id: Unique refund identifier.
- return_request: Reference to ReturnRequest.
- amount: Refund amount.
- refund_date: Refund date.
- status: Refund status.
- transaction_reference: Payment reference.

### InventoryDisposition
Stores decisions about returned inventory.
- return_line: Reference to ReturnLine.
- inspection: Related Inspection, when available.
- disposition_type: Inventory decision.
- quantity: Quantity processed.
- processed_date: Processing date.
- notes: Additional information.

### ReturnEvent
Maintains return activity history.
- return_request: Reference to ReturnRequest.
- event_type: Event category.
- description: Event details.
- actor: Person or system responsible.
- created_at: Event timestamp.

### GroundTruth
Stores expected decisions for labelled edge cases.
- return_request: Reference to ReturnRequest.
- issue_type: Edge-case category.
- expected_decision: Expected business decision.
- details: Additional explanation.
- created_at: Record creation timestamp.

## 3. Relationships

- Customer has many Orders.
- Order has many OrderLines.
- Order has many ReturnRequests.
- ReturnRequest has many ReturnLines.
- ReturnRequest has authorization information.
- ReturnAuthorization has shipment records.
- ReturnLine has inspection records.
- ReturnRequest has refund records.
- ReturnLine has inventory disposition records.
- ReturnRequest has many ReturnEvents.
- ReturnRequest has GroundTruth labels.

## 4. Data Integrity

The system uses primary keys, foreign keys, unique identifiers and Django model relationships to maintain data integrity.

## 5. Important Note

This dictionary describes the current database structure. It does not imply that every return business rule is automatically enforced.