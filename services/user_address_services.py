import constants
import logging
from models import user_models,order_models
from schemas import user_schemas
from fastapi import FastAPI, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from datetime import datetime
import constants
from pytz import timezone
now_utc = datetime.now(timezone('UTC'))

app = FastAPI()

logger = logging.getLogger(__name__)



def add_address_details(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    user = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()
    if not user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg
    if request.default == False:
        data = user_models.CustomerAddresses(customer_id=request.customer_id, full_name=request.full_name, contact=request.contact, house_no_building_name=request.house_no_building_name, road_name_Area=request.road_name_Area,
                                             landmark=request.landmark, country=request.country, region=request.region, town_city=request.town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude)
        db.merge(data)
        db.commit()

        data2 = user_schemas.CustomerAddressResponse2(customer_id=request.customer_id, full_name=request.full_name, contact=request.contact, house_no_building_name=request.house_no_building_name, road_name_Area=request.road_name_Area,
                                                      landmark=request.landmark, country=request.country, region=request.region, town_city=request.town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude)
        common_msg = user_schemas.ResponseCommonMessageSchema(
            status=status.HTTP_200_OK, message="Address Added Successfully!", data=data2)
        return common_msg

    else:

        data3 = db.query(user_models.User).filter(
            user_models.User.id == request.customer_id).first()
        data3.delivery_house_no_building_name = request.house_no_building_name
        data3.delivery_road_name_Area = request.road_name_Area
        data3.delivery_landmark = request.landmark
        data3.delivery_country = request.country
        data3.delivery_region = request.region
        data3.delivery_town_city = request.town_city
        data3.deliveryAddress_latitude = request.deliveryAddress_latitude
        data3.deliveryAddress_longitude = request.deliveryAddress_longitude
        data3.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
        db.merge(data3, data3.updated_at)
        db.commit()

        user_default_address = db.query(user_models.CustomerAddresses).filter(
            user_models.CustomerAddresses.customer_id == request.customer_id, user_models.CustomerAddresses.is_default == True).first()
        user_default_address.full_name = request.full_name
        user_default_address.contact = request.contact
        user_default_address.house_no_building_name = request.house_no_building_name
        user_default_address.road_name_Area = request.road_name_Area
        user_default_address.landmark = request.landmark
        user_default_address.country = request.country
        user_default_address.region = request.region
        user_default_address.town_city = request.town_city
        user_default_address.deliveryAddress_latitude = request.deliveryAddress_latitude
        user_default_address.deliveryAddress_longitude = request.deliveryAddress_longitude
        user_default_address.is_default = True
        db.merge(user_default_address)
        db.commit()

        data2 = user_schemas.CustomerAddressResponse2(customer_id=request.customer_id, full_name=request.full_name, contact=request.contact, house_no_building_name=request.house_no_building_name, road_name_Area=request.road_name_Area,
                                                      landmark=request.landmark, country=request.country, region=request.region, town_city=request.town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude)
        common_msg = user_schemas.ResponseCommonMessageSchema(
            status=status.HTTP_200_OK, message="Default Address Added Successfully!", data=data2)
        return common_msg


def get_all_address(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    user_address = db.execute(
        f'select * from {constants.Database_name}.customer_addresses where customer_id = "{customer_id}"')
    if user_address:
        address_list = []
        for i in user_address:
            data = user_schemas.CustomerAddressResponse(address_id=i.id, full_name=i.full_name, contact=i.contact, house_no_building_name=i.house_no_building_name, road_name_Area=i.road_name_Area, landmark=i.landmark,
                                                        country=i.country, region=i.region, town_city=i.town_city, deliveryAddress_latitude=i.deliveryAddress_latitude, deliveryAddress_longitude=i.deliveryAddress_longitude, is_default=i.is_default)
            address_list.append(data)
        response = user_schemas.ResponseAddressSchema(
            status=status.HTTP_200_OK, message="All addresses!", customer_id=customer_id, data=address_list)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User data doesn't exit")
        return common_msg


def update_address(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    db_user_update = db.query(user_models.CustomerAddresses).filter(
        user_models.CustomerAddresses.id == request.address_id).first()

    if not db_user_update:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Address Doesn't Exist!")
        return common_msg
    if request.is_default == True:
        user_default_address = db.query(user_models.CustomerAddresses).filter(
            user_models.CustomerAddresses.id == request.address_id, user_models.CustomerAddresses.is_default == True).first()
        if user_default_address:
            user_default_address.full_name = request.full_name
            user_default_address.contact = request.contact
            user_default_address.house_no_building_name = request.house_no_building_name
            user_default_address.road_name_Area = request.road_name_Area
            user_default_address.landmark = request.landmark
            user_default_address.country = request.country
            user_default_address.region = request.region
            user_default_address.town_city = request.town_city
            user_default_address.deliveryAddress_latitude = request.deliveryAddress_latitude
            user_default_address.deliveryAddress_longitude = request.deliveryAddress_longitude
            user_default_address.is_default = True
            user_default_address.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
            db.merge(user_default_address, user_default_address.updated_at)
            db.commit()

            data3 = db.query(user_models.User).filter(
                user_models.User.id == request.customer_id).first()
            data3.delivery_house_no_building_name = request.house_no_building_name
            data3.delivery_road_name_Area = request.road_name_Area
            data3.delivery_landmark = request.landmark
            data3.delivery_country = request.country
            data3.delivery_region = request.region
            data3.delivery_town_city = request.town_city
            data3.deliveryAddress_latitude = request.deliveryAddress_latitude
            data3.deliveryAddress_longitude = request.deliveryAddress_longitude
            data3.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
            db.merge(data3, data3.updated_at)
            db.commit()

        else:
            old_default_address = db.query(user_models.CustomerAddresses).filter(
                user_models.CustomerAddresses.customer_id == request.customer_id, user_models.CustomerAddresses.is_default == True).first()
            old_default_address.is_default = False
            old_default_address.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
            db.merge(old_default_address, old_default_address.updated_at)
            db.commit()

            db_user_update.full_name = request.full_name
            db_user_update.contact = request.contact
            db_user_update.house_no_building_name = request.house_no_building_name
            db_user_update.road_name_Area = request.road_name_Area
            db_user_update.landmark = request.landmark
            db_user_update.country = request.country
            db_user_update.region = request.region
            db_user_update.town_city = request.town_city
            db_user_update.deliveryAddress_latitude = request.deliveryAddress_latitude
            db_user_update.deliveryAddress_longitude = request.deliveryAddress_longitude
            db_user_update.is_default = True
            db_user_update.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
            db.merge(db_user_update, db_user_update.updated_at)
            db.commit()

            data3 = db.query(user_models.User).filter(
                user_models.User.id == request.customer_id).first()
            data3.delivery_house_no_building_name = request.house_no_building_name
            data3.delivery_road_name_Area = request.road_name_Area
            data3.delivery_landmark = request.landmark
            data3.delivery_country = request.country
            data3.delivery_region = request.region
            data3.delivery_town_city = request.town_city
            data3.deliveryAddress_latitude = request.deliveryAddress_latitude
            data3.deliveryAddress_longitude = request.deliveryAddress_longitude
            data3.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
            db.merge(data3, data3.updated_at)
            db.commit()

    else:

        db_user_update.full_name = request.full_name
        db_user_update.contact = request.contact
        db_user_update.house_no_building_name = request.house_no_building_name
        db_user_update.road_name_Area = request.road_name_Area
        db_user_update.landmark = request.landmark
        db_user_update.country = request.country
        db_user_update.region = request.region
        db_user_update.town_city = request.town_city
        db_user_update.deliveryAddress_latitude = request.deliveryAddress_latitude
        db_user_update.deliveryAddress_longitude = request.deliveryAddress_longitude
        db_user_update.is_default = False
        db_user_update.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
        db.merge(db_user_update, db_user_update.updated_at)
        db.commit()
        res_data = user_schemas.UpdateCustomerAddress(customer_id=request.customer_id, address_id=db_user_update.id, full_name=request.full_name, contact=request.contact, house_no_building_name=request.house_no_building_name, road_name_Area=request.road_name_Area,
                                                      landmark=request.landmark, country=request.country, region=request.region, town_city=request.town_city, is_default=False, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude)
        common_msg = user_schemas.Updateaddressschema(
            status=status.HTTP_200_OK, message="Address Updated Successfully !", data=res_data)
        return common_msg

    res_data = user_schemas.UpdateCustomerAddress(customer_id=request.customer_id, address_id=db_user_update.id, full_name=request.full_name, contact=request.contact, house_no_building_name=request.house_no_building_name, road_name_Area=request.road_name_Area,
                                                  landmark=request.landmark, country=request.country, region=request.region, town_city=request.town_city, is_default=True, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude)
    common_msg = user_schemas.Updateaddressschema(
        status=status.HTTP_200_OK, message="Address Updated Successfully !", data=res_data)
    return common_msg


def get_billing_address(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    user_address = db.execute(
        f'select * from {constants.Database_name}.customers_master where id = "{customer_id}"')
    if user_address:
        for i in user_address:
            data = user_schemas.ResponseBillingaddress(customer_id=i.id, first_name=i.first_name, last_name=i.last_name, billing_house_no_building_name=i.billing_house_no_building_name, billing_road_name_Area=i.billing_road_name_Area, billing_landmark=i.billing_landmark,
                                                       billing_country=i.billing_country, billing_region=i.billing_region, billing_town_city=i.billing_town_city, billlingAddress_Latitude=i.billlingAddress_Latitude, billingAddress_longitude=i.billingAddress_longitude)
        response = user_schemas.ResponseBillingaddressfinal(
            status=status.HTTP_200_OK, message="Billing Address!", data=data)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User data doesn't exit")
        return common_msg


def update_billing_address(request, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    db_user_update = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()

    if not db_user_update:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg

    db_user_update.billing_house_no_building_name = request.billing_house_no_building_name
    db_user_update.billing_road_name_Area = request.billing_road_name_Area
    db_user_update.billing_landmark = request.billing_landmark
    db_user_update.billing_country = request.billing_country
    db_user_update.billing_region = request.billing_region
    db_user_update.billing_town_city = request.billing_town_city
    db_user_update.billlingAddress_Latitude = request.billlingAddress_Latitude
    db_user_update.billingAddress_longitude = request.billingAddress_longitude
    db_user_update.updated_at = now_utc.astimezone(timezone(constants.Default_time_zone))
    db.merge(db_user_update, db_user_update.updated_at)
    db.commit()
    res_data = user_schemas.BillingAddressUpdate(customer_id=request.customer_id, billing_house_no_building_name=request.billing_house_no_building_name, billing_road_name_Area=request.billing_road_name_Area, billing_landmark=request.billing_landmark,
                                                 billing_country=request.billing_country, billing_region=request.billing_region, billing_town_city=request.billing_town_city, billlingAddress_Latitude=request.billlingAddress_Latitude, billingAddress_longitude=request.billingAddress_longitude)
    common_msg = user_schemas.ResponseBillingaddressupdate(
        status=status.HTTP_200_OK, message="Billing Address Updated Successfully !", data=res_data)
    return common_msg


def delete_customer_address(address_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    delete_address_data = db.query(user_models.CustomerAddresses).filter(
        user_models.CustomerAddresses.id == address_id).first()
    grocery_address = db.query(order_models.UserGrocery).filter(
        order_models.UserGrocery.address_id == address_id).first()
    if not delete_address_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Address Doesn't Exist!")
        return common_msg
    if grocery_address:
        grocery_id = grocery_address.id
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message=f"Your this address is exist in your grocery id = {grocery_id}, first delete this grocery!")
        return common_msg
    db.delete(delete_address_data)
    db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Address Deleted Successfully!")
    return common_msg

