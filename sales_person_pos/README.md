# POS Custom Features (Odoo 18)

## 💡 Overview
This Odoo module extends the Point of Sale (POS) functionality to allow POS users (cashiers) to select and assign the employee responsible for specific order lines. This feature is crucial for accurate sales attribution, commission calculation, and individual performance tracking.

## ✨ Features
* **Employee Assignment:** Adds a custom button/mechanism in the POS interface to select an employee for the current order line.
* **Backend Integration:** Links the selected employee to the `pos.order.line` model.
* **HR Dependency:** Requires the `hr` module for employee data.

## ⚙️ Installation
1. Clone this repository into your Odoo custom addons path.
2. Go to Odoo's Apps list, update the list, and search for 'POS Custom Features'.
3. Install the module.

## 🔗 Dependencies
* `point_of_sale`
* `hr`


## 👨‍💻 Author
Mahmoud Hawas
