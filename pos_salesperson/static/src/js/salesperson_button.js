/** pos_salesperson_button/static/src/js/salesperson_button.js **/
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { registry } from "@web/core/registry";

class SalespersonButton extends ControlButtons {
    setup() {
        super.setup();
    }
    onClick() {
        // Show popup with available salespersons
        this.showPopup("SelectionPopup", {
            title: "Select Salesperson",
            list: this.env.pos.db.get_salespersons().map(sp => ({
                id: sp.id,
                label: sp.name,
            })),
            confirm: (sp) => {
                this.currentOrder.set_salesperson(sp);
            },
        });
    }
}

// Register the button in POS registry
registry.category("pos_control_buttons").add("salesperson_button", SalespersonButton);
