import { PosDB } from "@point_of_sale/app/db";

PosDB.prototype.add_salespersons = function(users) {
    this._salespersons = users;
};

PosDB.prototype.get_salespersons = function() {
    return this._salespersons || [];
};
