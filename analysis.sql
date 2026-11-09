-- One row per assigned customer, including customers with no visit.
SELECT customer_id, segment, treatment, visits,
       gross_cents - variable_cost_cents AS pre_offer_cents,
       redeemed,
       gross_cents - variable_cost_cents - redeemed * :offer_cents
           - treatment * :contact_cents AS net_cents
FROM customers
ORDER BY customer_id;