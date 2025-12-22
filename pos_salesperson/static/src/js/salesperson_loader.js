import { PosGlobalState } from "@point_of_sale/app/store/pos_global_state";

PosGlobalState.prototype.load_salespersons = async function() {
    const salespersons = await this.env.services.rpc({
        model: 'res.users',
        method: 'search_read',
        args: [[['share', '=', false]], ['id', 'name']],
    });
    this.db.add_salespersons(salespersons);
};
