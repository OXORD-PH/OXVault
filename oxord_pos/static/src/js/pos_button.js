/** @odoo-module **/
console.log("POS SALESPERSON JS LOADED");

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { Order } from "@point_of_sale/app/store/models";

/* ------------------------------------------
   PATCH PRODUCT SCREEN (Button Click)
-------------------------------------------*/

patch(ProductScreen.prototype, {

    async onClickSalesperson() {

        const users = this.pos.models['res.users']?.getAll() || [];

        if (!users.length) {
            return;
        }

        const list = users.map(user => ({
            id: user.id,
            label: user.name,
            item: user,
        }));

        const { confirmed, payload } = await this.popup.add(SelectionPopup, {
            title: "Select Salesperson",
            list: list,
        });

        if (confirmed) {
            const order = this.pos.get_order();
            order.set_salesperson(payload);
        }
    },

});


/* ------------------------------------------
   PATCH ORDER MODEL (SAVE TO BACKEND)
-------------------------------------------*/

patch(Order.prototype, {

    setup() {
        super.setup(...arguments);
        this.salesperson = null;
    },

    set_salesperson(user) {
        this.salesperson = user;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.salesperson_id = this.salesperson ? this.salesperson.id : false;
        return json;
    },

});
