from models import order_models
from utility_services import common_services
import constants
from sqlalchemy.orm import Session


def update_inventory(order_id, product_id, product_quantity, db: Session):
    inventory = order_models.Inventory(order_id=order_id, quantity=product_quantity, inventory_type_id=3,
                                       product_id=product_id, warehouse_id=1, order_status="ordered", created_at=common_services.get_time())
    db.merge(inventory)
    db.commit()
    # Inverntory Update start
    try:
        product_type = db.execute(
            f"SELECT `inventory`.`inventory_type_id`, SUM(`inventory`.`quantity`) AS `inventory_quantity` FROM `inventory` WHERE `inventory`.`product_id` = {product_id} GROUP BY `inventory`.`inventory_type_id` ORDER BY `inventory`.`inventory_type_id` ASC")
        total_quantity = 0
        inventory_starting = 0
        inventory_received = 0
        inventory_shipped = 0
        inventory_cancelled = 0
        for quantity_cal in product_type:
            quantity = quantity_cal['inventory_quantity']
            if quantity_cal['inventory_type_id'] == 3:
                total_quantity -= quantity
                inventory_shipped = quantity
            else:
                total_quantity += quantity
                if quantity_cal['inventory_type_id'] == 1:
                    inventory_starting = quantity
                elif quantity_cal['inventory_type_id'] == 2:
                    inventory_received = quantity
                else:
                    inventory_cancelled = quantity
        timestamp = str(common_services.get_time())
        update_query = f"UPDATE {constants.Database_name}.products_master SET `quantity` = {total_quantity},`updated_at` = '{timestamp}',`inventory_starting` = {inventory_starting},`inventory_received` = {inventory_received},`inventory_shipped` = {inventory_shipped},`inventory_cancelled` = {inventory_cancelled},`inventory_onhand` = {total_quantity} WHERE `id` = {product_id};"
        db.execute(update_query)
        db.commit()
        return True
        # Inverntory Update end
    except Exception as e:
        print(e)
        return False
