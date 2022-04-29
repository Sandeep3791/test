import constants
import logging
from models import order_models
from schemas import user_schemas,cart_schemas
from fastapi import FastAPI, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from datetime import datetime


app = FastAPI()

logger = logging.getLogger(__name__)



def create_cart(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    data_exist = db.query(order_models.CustomerCart).filter(order_models.CustomerCart.customer_id == request.customer_id, order_models.CustomerCart.product_id == request.product_id).first()
    if data_exist:
        common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message="This products already available in your cart")
        return common_msg
    db_data = order_models.CustomerCart(
        customer_id=request.customer_id, product_id=request.product_id, product_quantity=request.product_quantity)
    db.merge(db_data)
    db.commit()
    common_msg = cart_schemas.CartResponseNew(status=status.HTTP_200_OK, message="Product added to cart Successfully!",
                                              customer_id=request.customer_id, product_id=request.product_id, product_quantity=request.product_quantity)
    return common_msg


def get_cart_product(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    user_cart = db.execute(
        f'select * from {constants.Database_name}.customer_cart where customer_id = {customer_id}')
    if user_cart.rowcount == 0:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No products available in cart!")
        return common_msg
    cart_list = []
    for var in user_cart:
        data = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {var.product_id} ")
        for i in data:
            # quantity_unit = i.quantity_unit_id
            # weight_unit = i.weight_unit_id
            quantity_unit = i.quantity_unit_id if i.quantity_unit_id else 1
            weight_unit = i.weight_unit_id if i.weight_unit_id else 1
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
                f"select image from {constants.Database_name}.product_images where product_id = {var.product_id}")
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
                        margin_value = (intial_price/100)*int(i.wayrem_margin)
                        updated_price = intial_price+margin_value
                    else:
                        updated_price = intial_price + float(i.wayrem_margin)
            var2 = i.id
            result = None
            rates = db.execute(
                f"select * from {constants.Database_name}.product_rating where product_id= {var2}")
            for rate in rates:
                result = rate.rating
            qty = int(i.quantity)
            qty_thresold = i.outofstock_threshold
            final_qty = qty
            data2 = cart_schemas.GetCartProducts(cart_id=var.id, product_id=var.product_id, product_quantity=var.product_quantity, stock_quantity=final_qty, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description,
                                                 quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[0], price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list, rating=result)
        
        cart_list.append(data2)
    response = cart_schemas.GetCartResponse(
        status=status.HTTP_200_OK, message="All Cart Products!", customer_id=customer_id, data=cart_list)
    # return response
    return response


def update_cart_product(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    db_cart_update = db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.id == request.cart_id).first()

    db_cart_update.product_quantity = request.product_quantity
    db_cart_update.updated_at = datetime.now()
    db.merge(db_cart_update, db_cart_update.updated_at)
    db.commit()
    res_data = cart_schemas.UpdateCartProducts(
        cart_id=request.cart_id, product_id=request.product_id, product_quantity=request.product_quantity)
    common_msg = cart_schemas.CartUpdateRes(
        status=status.HTTP_200_OK, message="Cart Updated Successfully !", data=res_data)
    return common_msg


def delete_cart(cart_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    delete_product = db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.id == cart_id).first()
    if not delete_product:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="cart id not found!")
        return common_msg
    db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.id == cart_id).delete(synchronize_session=False)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Cart Product deleted Successfully!", data="null")
    return common_msg


def clear_cart(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    delete_product = db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.customer_id == customer_id).all()
    if not delete_product:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="cart id not found!")
        return common_msg
    db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.customer_id == customer_id).delete(synchronize_session=False)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Cart cleared Successfully!", data="null")
    return common_msg


def add_multiple_products(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    cart_exist = db.query(order_models.CustomerCart).filter(
        order_models.CustomerCart.customer_id == request.customer_id).all()
    if cart_exist:
        for data in cart_exist:
            db.delete(data)
            db.commit()
    products_list = []
    for j in request.products:
        db_data = order_models.CustomerCart(
            customer_id=request.customer_id, product_id=j.product_id, product_quantity=j.product_quantity)
        db.merge(db_data)
        db.commit()

        data2 = user_schemas.AddMultipleProducts(
            product_id=j.product_id, product_quantity=j.product_quantity)
        products_list.append(data2)
    common_msg = user_schemas.ResponseCartMultipleProducts(status=status.HTTP_200_OK, message="Product added to cart Successfully!",
                                                           customer_id=request.customer_id, products=products_list)
    return common_msg

