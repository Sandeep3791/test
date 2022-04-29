import constants
import logging
from models import user_models,order_models
from schemas import user_schemas,grocery_schemas
from fastapi import FastAPI, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from datetime import datetime


app = FastAPI()

logger = logging.getLogger(__name__)


def create_user_grocery(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    user = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()
    if not user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Invalid User Id!")
        return common_msg

    if user.verification_status == "active":

        user_address = db.query(user_models.CustomerAddresses).filter(user_models.CustomerAddresses.id ==
                                                                      request.address_id, user_models.CustomerAddresses.customer_id == request.customer_id).first()
        if not user_address:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_200_OK, message="Invalid Address Id For This User!")
            return common_msg
        data = order_models.UserGrocery(grocery_name=request.grocery_name, description=request.description,
                                       customer_id=request.customer_id, address_id=request.address_id)
        db.merge(data)
        db.commit()
        last_record = db.execute(
            f'select * from {constants.Database_name}.grocery_master ORDER BY id DESC LIMIT 1')
        for i in last_record:
            last_id = i.id

        res_data = grocery_schemas.CreateGrocerySchema(id=last_id, customer_id=request.customer_id,
                                                    address_id=request.address_id, grocery_name=request.grocery_name, description=request.description)
        common_msg = grocery_schemas.CreateGroceryResponse(
            status=status.HTTP_200_OK, message="Grocery Created Successfully!", data=res_data)
        return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order")
        return common_msg


def update_user_grocery(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    update_grocery = db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.id == request.grocery_id).first()
    if not update_grocery:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Invalid Grocery Id!")
        return common_msg
    update_grocery.grocery_name = request.grocery_name
    update_grocery.description = request.description
    update_grocery.address_id = request.address_id
    update_grocery.updated_at = datetime.now()
    db.merge(update_grocery, update_grocery.updated_at)
    db.commit()
    res_data = grocery_schemas.UpdateGrocerySchemas(
        grocery_id=request.grocery_id, grocery_name=update_grocery.grocery_name, description=update_grocery.description, address_id=request.address_id)
    common_msg = grocery_schemas.UpdateGroceryResponse(
        status=status.HTTP_200_OK, message="Grocery Updated Successfully!", data=res_data)
    return common_msg


def delete_user_grocery(grocery_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    delete_grocery = db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.id == grocery_id).first()
    if not delete_grocery:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Grocery Id Doesn't Exist!")
        return common_msg
    recurrent_grocery = db.query(order_models.RecurrenceGrocery).filter(
        order_models.RecurrenceGrocery.grocery_id == grocery_id).all()
    if recurrent_grocery:
        for data in recurrent_grocery:
            db.delete(data)
            db.commit()
    db.query(order_models.GroceryProducts).filter(
        order_models.GroceryProducts.grocery_id == grocery_id).delete(synchronize_session=False)
    db.commit()
    db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.id == grocery_id).delete(synchronize_session=False)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Grocery Deleted Successfully!")
    return common_msg


def get_all_grocery(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    grocery_details = db.execute(
        f'select * from {constants.Database_name}.grocery_master where customer_id ="{customer_id}"')
    if grocery_details.rowcount > 0:
        grocery_list = []
        for data in grocery_details:
            grocery_recurrent = db.query(order_models.RecurrenceGrocery).filter(
                order_models.RecurrenceGrocery.grocery_id == data.id).first()
            try:
                if grocery_recurrent.status == True:
                    a = grocery_recurrent.recurrence_nextdate
                    next_date = str(datetime.fromisoformat(a).date())
                else:
                    next_date = None
            except:
                next_date = None
            grocery_products = db.query(order_models.GroceryProducts).filter(
                order_models.GroceryProducts.grocery_id == data.id).all()
            count_value = len(grocery_products)
            res_data = grocery_schemas.ListGrocerDetailsResponse(grocery_id=data.id, product_count=count_value, customer_id=data.customer_id,
                                                              address_id=data.address_id, grocery_name=data.grocery_name, description=data.description, recurrence_next_date=next_date)
            grocery_list.append(res_data)
        common_msg = grocery_schemas.ListGroceryDetails(
            status=status.HTTP_200_OK, message="Grocery details", data=grocery_list)
        return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="This customer id doesn't have any grocery!")
        return common_msg


def create_grocery_products(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    create_products = db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.id == request.grocery_id).first()
    if not create_products:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Invalid Grocery Id")
        return common_msg
    product_exist = db.query(order_models.GroceryProducts).filter(
        order_models.GroceryProducts.grocery_id == request.grocery_id).all()
    if product_exist:
        for j in product_exist:
            db.delete(j)
            db.commit()

    result = []
    for i in request.products:
        match_products = db.execute(
            f'select * from {constants.Database_name}.products_master where id ="{i.product_id}" and publish = {True}')
        if match_products.rowcount <= 0:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message=f'Product Id {i.product_id} is Not Found!')
            return common_msg

        db_data = order_models.GroceryProducts(
            grocery_id=request.grocery_id, product_id=i.product_id, product_qty=i.product_qty)
        db.merge(db_data)
        db.commit()
        product_res = grocery_schemas.GroceryProductsListResponse(
            product_id=i.product_id, product_qty=i.product_qty)
        result.append(product_res)
    common_msg = grocery_schemas.CreateGroceryProdResponse(
        status=status.HTTP_200_OK, message="Products created Successfully for this grocery!", grocery_id=request.grocery_id, products=result)
    return common_msg


def get_grocery_products_details(grocery_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    grocery_products = db.execute(
        f'select * from {constants.Database_name}.grocery_products where grocery_id ="{grocery_id}"')
    if grocery_products.rowcount <= 0:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No grocery products found")
        return common_msg
    grocery_addr = db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.id == grocery_id).first()
    grocery_address_id = grocery_addr.address_id
    grocery_recurrency = db.query(order_models.RecurrenceGrocery).filter(
        order_models.RecurrenceGrocery.grocery_id == grocery_id).first()
    if grocery_recurrency:
        recurrenttype = grocery_recurrency.recurrenttype
        recurrence_startdate = grocery_recurrency.recurrence_startdate
        recurrence_value = db.query(order_models.RecurrentType).filter(
            order_models.RecurrentType.id == recurrenttype).first()
        recurrence_type_value = recurrence_value.name
        rec_status = grocery_recurrency.status
        recurrent_id = grocery_recurrency.id
    else:
        recurrence_type_value = None
        rec_status = None
        recurrence_startdate = None
        recurrent_id = None
    grocery_name = grocery_addr.grocery_name
    description = grocery_addr.description

    list_data = []
    for grocery_product in grocery_products:
        data = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {grocery_product.product_id} and publish = {True}")
        for i in data:
            quantity_unit = i.quantity_unit_id if i.quantity_unit_id else 1
            weight_unit = i.weight_unit_id if i.weight_unit_id else 1
            # quantity_unit = i.quantity_unit_id
            # weight_unit = i.weight_unit_id
            if i.primary_image:
                primary_img = i.primary_image
                # img_name = primary_img.split("/")[-1]
                image_path = constants.IMAGES_DIR_PATH + primary_img
            else:
                image_path = "null"

            unit1 = db.execute(
                f"select unit_name from {constants.Database_name}.unit_master where id = {quantity_unit}")
            unit2 = db.execute(
                f"select unit_name from {constants.Database_name}.unit_master where id = {weight_unit}")

            prod_images = db.execute(
                f"select image from {constants.Database_name}.product_images where product_id = {i.id}")
            image_list = []
            for image in prod_images:
                a = image[0]
                # update_img = a.split("/")[-1]
                upd_image_path = constants.IMAGES_DIR_PATH + a
                image_list.append(upd_image_path)

            for j in unit1:
                for k in unit2:
                    intial_price = float(i.price)
                    wayrem_margin = i.wayrem_margin if i.wayrem_margin else 0
                    if i.margin_unit == '%':
                        margin_value = (intial_price/100)*int(wayrem_margin)
                        updated_price = intial_price+margin_value
                    else:
                        updated_price = intial_price + float(wayrem_margin)

                    product_id = i.id
                    product_category = db.execute(
                        f"select * from {constants.Database_name}.products_master_category where products_id = {product_id}")
                    if product_category:
                        prod_category_list = []
                        for categories in product_category:
                            product_category_name = db.execute(
                                f"select * from {constants.Database_name}.categories_master where id = {categories.categories_id}")
                            for name in product_category_name:
                                catg_name = name.name
                                prod_category_list.append(catg_name)
                    else:
                        prod_category_list = []
                qty = int(i.quantity)
                qty_thresold = i.outofstock_threshold
                final_qty = qty
                res_data = grocery_schemas.GroceryProdResp(product_id=i.id, product_qty=grocery_product.product_qty, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty,
                                                        quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[0], categories=prod_category_list, price=updated_price, discount=i.discount,  discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list)
                list_data.append(res_data)
    data2 = grocery_schemas.GroceryRecurrenceprod(grocery_id=grocery_id, grocery_name=grocery_name, description=description, address_id=grocery_address_id,
                                               recurrent_id=recurrent_id, recurrenttype=recurrence_type_value, recurrence_startdate=recurrence_startdate, recurrence_status=rec_status, products=list_data)

    common_msg = grocery_schemas.ResponseCommonMessageProducts(
        status=status.HTTP_200_OK, message="All Products of Grocery!", data=data2)
    return common_msg


def update_product_quantity(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    product_update_qty = db.query(order_models.GroceryProducts).filter(
        order_models.GroceryProducts.grocery_id == request.grocery_id, order_models.GroceryProducts.product_id == request.product_id).first()
    if not product_update_qty:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Invalid Grocery Id")
        return common_msg
    product_update_qty.grocry_id = request.grocery_id
    product_update_qty.product_id = request.product_id
    product_update_qty.product_qty = request.product_qty
    db.merge(product_update_qty)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Quantity Updated Successfully")
    return common_msg


def delete_grocery_products(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    del_prod = db.query(order_models.GroceryProducts).filter(order_models.GroceryProducts.grocery_id ==
                                                            request.grocery_id, order_models.GroceryProducts.product_id == request.product_id).first()
    if not del_prod:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Invalid Grocery Id Or Product_id")
        return common_msg
    db.query(order_models.GroceryProducts).filter(order_models.GroceryProducts.grocery_id == request.grocery_id,
                                                 order_models.GroceryProducts.product_id == request.product_id).delete(synchronize_session=False)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Product deleted Successfully!")
    return common_msg

