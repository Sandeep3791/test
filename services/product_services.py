import constants
import logging
from models import user_models,product_models
from schemas import user_schemas,product_schemas
from services import user_services
from fastapi import FastAPI, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
import uuid


app = FastAPI()

logger = logging.getLogger(__name__)



def get_product_details(customer_id, product_id, db: Session):

    data = db.execute(
        f"select * from {constants.Database_name}.products_master where id = {product_id}")
    if data.rowcount <= 0:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Products Available!")
        return common_msg

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
            f"select image from {constants.Database_name}.product_images where product_id = {product_id}")
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
                    abc = intial_price+margin_value
                    updated_price = round(abc,2)
                else:
                    cde = intial_price + float(wayrem_margin)
                    # cde = intial_price + float(i.wayrem_margin)
                    updated_price = round(cde,2)

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
                user_fav_prod = db.query(product_models.FavoriteProduct).filter(
                    product_models.FavoriteProduct.product_id == product_id, product_models.FavoriteProduct.customer_id == customer_id).first()
                if user_fav_prod:
                    favorite = True
                    fav_uuid = user_fav_prod.id
                else:
                    favorite = False
                    fav_uuid = None

                var = i.id

                ratings = db.execute(
                    f"select * from {constants.Database_name}.product_rating where product_id= {var}")
                if ratings:
                    result = None
                    for rating in ratings:
                        result = rating.rating

                reviews = db.execute(
                    f"select * from {constants.Database_name}.rating_review where product_id= {var}")
                list2 = []
                if reviews:
                    for review in reviews:
                        customer_data = db.query(user_models.User).filter(
                            user_models.User.id == review.customer_id).first()
                        fname = customer_data.first_name
                        lname = customer_data.last_name
                        full_name = fname+lname
                        review_date = str(
                            review.date.strftime("%Y-%m-%d %H:%M:%S"))
                        try:
                            if customer_data.profile_pic:
                                customer_id = review.customer_id
                                data = user_services.download_profile_picture(
                                    customer_id, db)
                                x = dict(data.data)
                                file_path = x.get("file_path")
                            else:
                                file_path = None
                        except:
                            file_path = None

                        var = product_schemas.GetReview(
                            customer_id=review.customer_id, customer_name=full_name, customer_profile=file_path, rating=review.rating, review=review.review, date=review_date)
                        list2.append(var)

                qty = int(i.quantity)
                qty_thresold = i.outofstock_threshold
                final_qty = qty
                res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                    0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=fav_uuid, primary_image=image_path, images=image_list, rating=result, review=list2)
    common_msg = product_schemas.GetProductDetails(
        status=status.HTTP_200_OK, message="Products Details", data=res_data)
    return common_msg


def get_all_products(offset, customer_id, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])
    data = db.execute(
        f"select * from {constants.Database_name}.products_master where publish = {True} limit {offset_int},{limit_val}")

    fav_product_data = db.execute(
        f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {constants.Database_name}.products_master t1 inner join {constants.Database_name}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} and t1.publish = {True} ;")

    if not data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Products Available!")
        return common_msg

    fav_id_list = []
    for favorite in fav_product_data:
        fav_prod_id = int(favorite.product_id)
        fav_id_list.append(fav_prod_id)

    list_data = []
    for i in data:
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
                if i.margin_unit == '%':
                    margin_value = (intial_price/100)*int(i.wayrem_margin)
                    abc = intial_price+margin_value
                    updated_price = round(abc, 2)
                else:
                    wayrem_margin = i.wayrem_margin if i.wayrem_margin else 0
                    cde = intial_price + float(wayrem_margin)
                    # cde = intial_price + float(i.wayrem_margin)
                    updated_price = round(cde, 2)

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

        for favr_id in fav_id_list:
            fav_product_uuid = db.query(product_models.FavoriteProduct).filter(
                product_models.FavoriteProduct.product_id == favr_id, product_models.FavoriteProduct.customer_id == customer_id).first()
            if favr_id == product_id:
                favorite = True
                favorite_product_id = fav_product_uuid.id
                break
            favorite = False
            favorite_product_id = None
        if fav_product_data.rowcount == 0:
            favorite = False
            favorite_product_id = None

        var = i.id
        result = None
        rates = db.execute(
            f"select * from {constants.Database_name}.product_rating where product_id= {var}")
        for rate in rates:
            result = rate.rating

        qty = int(i.quantity)
        qty_thresold = i.outofstock_threshold
        final_qty = qty
        res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                  0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=favorite_product_id, primary_image=image_path, images=image_list, rating=result)
        list_data.append(res_data)
    common_msg = product_schemas.GetAllProducts(
        status=status.HTTP_200_OK, message="All Products List", data=list_data)
    return common_msg


def get_category_products(customer_id, category_id, offset, db: Session):

    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])

    data = db.execute(
        f"select * from {constants.Database_name}.products_master t1 inner join  {constants.Database_name}.products_master_category t2  on t2.categories_id = {category_id} where t1.id = t2.products_id and t1.publish = {True} limit {offset_int},{limit_val};")

    fav_product_data = db.execute(
        f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {constants.Database_name}.products_master t1 inner join {constants.Database_name}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} and t1.publish = {True} ;")
    fav_id_list = []
    for favorite in fav_product_data:
        fav_prod_id = int(favorite.product_id)
        fav_id_list.append(fav_prod_id)

    list_data = []
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

                product_id = i.products_id
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

                for favr_id in fav_id_list:
                    fav_product_uuid = db.query(product_models.FavoriteProduct).filter(
                        product_models.FavoriteProduct.product_id == favr_id, product_models.FavoriteProduct.customer_id == customer_id).first()
                    if favr_id == product_id:
                        favorite = True
                        favorite_product_id = fav_product_uuid.id
                        break
                    favorite = False
                    favorite_product_id = None
                if fav_product_data.rowcount == 0:
                    favorite = False
                    favorite_product_id = None

            var = i.id
            result = None
            rates = db.execute(
                f"select * from {constants.Database_name}.product_rating where product_id= {var}")
            for rate in rates:
                result = rate.rating

            qty = int(i.quantity)
            qty_thresold = i.outofstock_threshold
            final_qty = qty
            res_data = product_schemas.AllProductDetails(id=i.products_id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                      0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=favorite_product_id, primary_image=image_path, images=image_list, rating=result)
            list_data.append(res_data)
    common_msg = product_schemas.GetAllProducts(
        status=status.HTTP_200_OK, message="Category Products List", data=list_data)
    return common_msg


def get_all_categories(db: Session):

    category_data = db.execute(
        f'select * from {constants.Database_name}.categories_master')
    if category_data.rowcount > 0:
        cat_list = []
        for data in category_data:
            path = data.image
            if path:
                category_image = constants.IMAGES_DIR_PATH + path
            else:
                category_image = "null"
            res_data = product_schemas.Allcategories(
                category_id=data.id, category_name=data.name, category_tags=data.tag, category_image=category_image)
            cat_list.append(res_data)
        common_msg = product_schemas.Getcategories(
            status=status.HTTP_200_OK, message="Categories details", data=cat_list)
        return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No categories found!")
        return common_msg


def get_best_selling_products(db: Session):
    
    data = db.execute(
        f"SELECT product_id, count(product_id) FROM {constants.Database_name}.order_details group by product_id order by count(product_id) desc limit 0,20;")
    if not data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Products Available!")
        return common_msg
    list_data = [i[0] for i in data]
    products_list = []
    for best_product_id in list_data:
        product = db.execute(
            f"SELECT * FROM {constants.Database_name}.products_master where id={best_product_id} and publish = {True};")
        for i in product:
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

                    var = i.id
                    result = None
                    rates = db.execute(
                        f"select * from {constants.Database_name}.product_rating where product_id= {var}")
                    for rate in rates:
                        result = rate.rating

                    qty = int(i.quantity)
                    qty_thresold = i.outofstock_threshold
                    final_qty = qty
                    res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                              0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list, rating=result)
                    products_list.append(res_data)
    common_msg = product_schemas.GetAllProducts(
        status=status.HTTP_200_OK, message="All Best Selling Products List", data=products_list)
    return common_msg


def get_featured_products(customer_id, offset, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])

    fav_product_data = db.execute(
        f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {constants.Database_name}.products_master t1 inner join {constants.Database_name}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} and t1.publish = {True} ;")
    fav_id_list = []
    for favorite in fav_product_data:
        fav_prod_id = int(favorite.product_id)
        fav_id_list.append(fav_prod_id)

    data = db.execute(
        f"select * from {constants.Database_name}.products_master where feature_product = {True} and publish = {True} limit {offset_int},{limit_val}")
    if not data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Products Available!")
        return common_msg
    list_data = []
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

                for favr_id in fav_id_list:
                    fav_product_uuid = db.query(product_models.FavoriteProduct).filter(
                        product_models.FavoriteProduct.product_id == favr_id, product_models.FavoriteProduct.customer_id == customer_id).first()
                    if favr_id == product_id:
                        favorite = True
                        favorite_product_id = fav_product_uuid.id
                        break
                    favorite = False
                    favorite_product_id = None
                if fav_product_data.rowcount == 0:
                    favorite = False
                    favorite_product_id = None

                var = i.id
                result = None
                rates = db.execute(
                    f"select * from {constants.Database_name}.product_rating where product_id= {var}")
                for rate in rates:
                    result = rate.rating

                qty = int(i.quantity)
                qty_thresold = i.outofstock_threshold
                final_qty = qty
                res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                          0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=favorite_product_id, primary_image=image_path, images=image_list, rating=result)
                list_data.append(res_data)
    common_msg = product_schemas.GetAllProducts(
        status=status.HTTP_200_OK, message="All Products List", data=list_data)
    return common_msg


def Favorite_Product(request, db: Session):
    
    match_products = db.execute(
        f'select * from {constants.Database_name}.products_master where id ="{request.product_id}" and publish = {True}')
    prod_avail = db.query(product_models.FavoriteProduct).filter(product_models.FavoriteProduct.product_id ==
                                                              request.product_id, product_models.FavoriteProduct.customer_id == request.customer_id).first()
    if not prod_avail:
        if match_products.rowcount > 0:
            id = str(uuid.uuid4())
            new_data = product_models.FavoriteProduct(
                id=id, customer_id=request.customer_id, product_id=request.product_id, product_qty=request.product_qty)

            db.merge(new_data)
            db.commit()
            result = product_schemas.FavResponse(
                id=id, customer_id=request.customer_id, product_id=request.product_id, product_qty=request.product_qty)
            common_msg = product_schemas.Addfavresponse(
                status=status.HTTP_200_OK, message="favorite Product added Successfully!", data=result)
            return common_msg

        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_200_OK, message="the Product id is not available")
            return common_msg

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="this Product is already available in your favorites")
        return common_msg


def get_favorite_product_details(customer_id, db: Session):
    
    products = db.execute(
        f'select * from {constants.Database_name}.Favorite_Product where customer_id = "{customer_id}"')
    if products.rowcount==0:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="No favourite products availabe!")
        return common_msg
    product_list_data = []
    for var in products:
        data = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {var.product_id} and publish = {True}")
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
                        margin_value = (intial_price/100)*int(wayrem_margin)
                        updated_price = intial_price+margin_value
                    else:
                        updated_price = intial_price + float(wayrem_margin)
            var2 = i.id
            result = None
            rates = db.execute(
                f"select * from {constants.Database_name}.product_rating where product_id= {var2}")
            for rate in rates:
                result = rate.rating

            qty = int(i.quantity)
            qty_thresold = i.outofstock_threshold
            final_qty = qty
            data2 = product_schemas.FavoriteProduct(favorite_product_id=var.id, product_id=var.product_id, product_qty=final_qty, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description,
                                                 quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[0], price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list, rating=result)
        product_list_data.append(data2)
    response = product_schemas.FavoriteProductResponse(
        status=status.HTTP_200_OK, message="All Favorite Products!", customer_id=customer_id, data=product_list_data)
    return response


def update_favorite_product(request, db: Session):
    
    update_product = db.query(product_models.FavoriteProduct).filter(
        product_models.FavoriteProduct.customer_id == request.customer_id).first()
    if not update_product:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Invalid Id!")
        return common_msg

    update_product.customer_id = request.customer_id
    update_product.product_id = request.product_id
    update_product.product_qty = request.product_qty
    db.merge(update_product)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Product updated successfully")
    return common_msg


def delete_favorite_product(id, db: Session):
    
    delete_product = db.query(product_models.FavoriteProduct).filter(
        product_models.FavoriteProduct.id == id).first()
    if not delete_product:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="the Product id is not available")
        return common_msg
    db.query(product_models.FavoriteProduct).filter(
        product_models.FavoriteProduct.id == id).delete(synchronize_session=False)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Deleted Successfully!")
    return common_msg


def create_product_rating(request, db: Session):
    
    db_update_rating = db.query(product_models.RatingReview).filter(product_models.RatingReview.customer_id ==
                                                                 request.customer_id, product_models.RatingReview.product_id == request.product_id).first()
    x = 0
    if db_update_rating:
        db_update_rating.customer_id = request.customer_id
        db_update_rating.product_id = request.product_id
        db_update_rating.rating = request.rating,
        db_update_rating.review = request.review
        x += 1
        db.merge(db_update_rating)
        db.commit()
    else:
        data = product_models.RatingReview(
            customer_id=request.customer_id, product_id=request.product_id, rating=request.rating, review=request.review)
        db.merge(data)
        db.commit()

    res_data = product_schemas.CreateRating(
        customer_id=request.customer_id, product_id=request.product_id, rating=request.rating, review=request.review)

    message = "Rating Updated Successfully" if x == 1 else "Rating Given Successfully"

    response = product_schemas.CreateRatingResponse(
        status=status.HTTP_200_OK, message=message, data=res_data)

    product_count = 0
    sum = 0
    main = 0
    review_count = 0
    data1 = db.execute(
        f'SELECT * FROM {constants.Database_name}.rating_review')
    for data in data1:
        if data.product_id == request.product_id:
            product_count = product_count+1
            sum = sum+data.rating
            if data.review != None:
                review_count = review_count + 1

    main = sum/product_count

    db_update_avg_rating = db.query(product_models.ProductRating).filter(
        product_models.ProductRating.product_id == request.product_id).first()
    if db_update_avg_rating:
        db_update_avg_rating.rating = main
        db_update_avg_rating.total_ratings = product_count
        db_update_avg_rating.total_reviews = review_count
        db.merge(db_update_avg_rating)
        db.commit()
    else:
        new_rating = product_models.ProductRating(
            product_id=request.product_id,
            rating=main,
            total_ratings=product_count,
            total_reviews=review_count
        )
        db.merge(new_rating)
        db.commit()

    return response


def search_filter_products(offset ,customer_id, start_price, end_price, discount, featured, rating, newest, category, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])

    query = f"select * from {constants.Database_name}.products_master where "
    query += f" publish = {True}"

    if start_price:
        query += f" and price > {start_price}"
    if end_price:
        query += f" and price < {end_price}"
    if discount:
        query += f" and discount > {discount}"
    if featured:
        query += f" and feature_product = true"
    elif featured == False:
        query += f" and feature_product = false"
    if category:
        query += f" and id in (select products_id from {constants.Database_name}.products_master_category where categories_id in ({category}))"
    if newest:
        query += f" order by updated_at ASC "

    rating_request = rating
    result = None
    
    query += f" limit {offset_int},{limit_val}"

    data = db.execute(query)

    fav_product_data = db.execute(
        f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {constants.Database_name}.products_master t1 inner join {constants.Database_name}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} and t1.publish = {True} ;")

    fav_id_list = []
    for favorite in fav_product_data:
        fav_prod_id = int(favorite.product_id)
        fav_id_list.append(fav_prod_id)

    list_data = []
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
        ratings = db.execute(
            f"select * from {constants.Database_name}.product_rating where product_id= {i.id}")
        if ratings:
            for rating in ratings:
                result = rating.rating

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
        for favr_id in fav_id_list:
            fav_product_uuid = db.query(product_models.FavoriteProduct).filter(
                product_models.FavoriteProduct.product_id == favr_id, product_models.FavoriteProduct.customer_id == customer_id).first()
            if favr_id == product_id:
                favorite = True
                favorite_product_id = fav_product_uuid.id
                break
            favorite = False
            favorite_product_id = None
        if fav_product_data.rowcount == 0:
            favorite = False
            favorite_product_id = None
        var = i.id
        ratings = db.execute(
            f"select * from {constants.Database_name}.product_rating where product_id= {var}")
        if ratings:
            result = None
            for rating in ratings:
                result = rating.rating

        reviews = db.execute(
            f"select * from {constants.Database_name}.rating_review where product_id= {var}")
        list2 = []
        if reviews:
            for review in reviews:
                customer_data = db.query(user_models.User).filter(
                    user_models.User.id == review.customer_id).first()
                fname = customer_data.first_name
                lname = customer_data.last_name
                full_name = fname+lname
                review_date = str(
                    review.date.strftime("%Y-%m-%d %H:%M:%S"))
                var = product_schemas.GetReview(
                    customer_id=review.customer_id, customer_name=full_name, rating=review.rating, review=review.review, date=review_date)
                list2.append(var)
        qty = int(i.quantity)
        qty_thresold = i.outofstock_threshold
        final_qty = qty
        res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                  0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=favorite_product_id, primary_image=image_path, rating=result, review=list2, images=image_list)
        if result:
            if rating_request:
                if result > 0:
                    list_data.append(res_data)
            elif rating_request == False:
                if result == 0.0:
                    list_data.append(res_data)
            else:
                list_data.append(res_data)
        else:
            list_data.append(res_data)

    common_msg = product_schemas.GetAllProducts(
        status=status.HTTP_200_OK, message="Filtered Products List", data=list_data)
    return common_msg


def search_products_name(offset,customer_id, name, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])

    query = f"SELECT * FROM  {constants.Database_name}.products_master where meta_key REGEXP '{name}$' or name LIKE '%{name}%' and publish = {True} limit {offset_int},{limit_val} "
    data = db.execute(query)

    fav_product_data = db.execute(
        f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {constants.Database_name}.products_master t1 inner join {constants.Database_name}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} and t1.publish = {True} ;")

    fav_id_list = []
    for favorite in fav_product_data:
        fav_prod_id = int(favorite.product_id)
        fav_id_list.append(fav_prod_id)
    list_data = []
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
                    f"select * from {constants.Database_name}.products_master_category where products_id = {product_id} ")
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
        for favr_id in fav_id_list:
            fav_product_uuid = db.query(product_models.FavoriteProduct).filter(
                product_models.FavoriteProduct.product_id == favr_id, product_models.FavoriteProduct.customer_id == customer_id).first()
            if favr_id == product_id:
                favorite = True
                favorite_product_id = fav_product_uuid.id
                break
            favorite = False
            favorite_product_id = None
        if fav_product_data.rowcount == 0:
            favorite = False
            favorite_product_id = None
        var = i.id
        ratings = db.execute(
            f"select * from {constants.Database_name}.product_rating where product_id= {var}")
        if ratings:
            result = None
            for rating in ratings:
                result = rating.rating

        reviews = db.execute(
            f"select * from {constants.Database_name}.rating_review where product_id= {var}")
        list2 = []
        if reviews:
            for review in reviews:
                customer_data = db.query(user_models.User).filter(
                    user_models.User.id == review.customer_id).first()
                fname = customer_data.first_name
                lname = customer_data.last_name
                full_name = fname+lname
                review_date = str(
                    review.date.strftime("%Y-%m-%d %H:%M:%S"))
                var = product_schemas.GetReview(
                    customer_id=review.customer_id, customer_name=full_name, rating=review.rating, review=review.review, date=review_date)
                list2.append(var)
        qty = int(i.quantity)
        qty_thresold = i.outofstock_threshold
        final_qty = qty
        res_data = product_schemas.AllProductDetails(id=i.id, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description, quantity=final_qty, quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[
                                                  0], categories=prod_category_list, price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, favorite=favorite, favorite_product_uuid=favorite_product_id, rating=result, review=list2, primary_image=image_path, images=image_list)
        list_data.append(res_data)
    if list_data:
        common_msg = product_schemas.GetAllProducts(
            status=status.HTTP_200_OK, message="Filtered Products List", data=list_data)
        return common_msg
    else:
        common_msg = product_schemas.GetAllProducts(
            status=status.HTTP_200_OK, message="No Products available", data=list_data)
        return common_msg

