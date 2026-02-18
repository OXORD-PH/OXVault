/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useListener } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import Registries from "@point_of_sale/app/registries";

export class SalespersonButton extends ProductScreen.ControlButton {
    setup() {
        super.setup();
        useListener('click', this.onClick);
    }

    async onClick() {
        const users = this.env.pos.users || [];

        if (users.length === 0) {
            alert("No internal users available as salespersons.");
            return;
        }

        const list = users.map(user => ({
            id: user.id,
            label: user.name,
            item: user,
        }));

        const { confirmed, payload } = await this.showPopup(SelectionPopup, {
            title: "Select Salesperson",
            list: list,
        });

        if (confirmed) {
            const order = this.env.pos.get_order();
            order.salesperson_id = [payload.id, payload.name];
            // No direct DOM update needed; OWL will re-render using getter
        }
    }

    get currentSalesperson() {
        const order = this.env.pos.get_order();
        return order?.salesperson_id?.[1] || "Salesperson";
    }
}

// OWL template name
SalespersonButton.template = "SalespersonButton";

// Register button
ProductScreen.addControlButton({
    component: SalespersonButton,
    condition: () => true,
});

Registries.Component.add(SalespersonButton);
