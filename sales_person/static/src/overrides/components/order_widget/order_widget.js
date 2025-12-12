/** @odoo-module **/

import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";

patch(OrderWidget.prototype, "pos_sales_person/OrderWidget", {
    // You can override methods here if needed
});
