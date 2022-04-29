from constants import Database_name, IMAGES_DIR_PATH


class Product:
    DATABASE_NAME = Database_name
    IMAGE_PATH = IMAGES_DIR_PATH
    db = None

    def __init__(self, db):
        self.db = db

    def db_data(self, query):
        return self.db.execute(query)

    def get_details(self, table_name, key, lookup="id"):
        query = f"SELECT * FROM {self.DATABASE_NAME}.{table_name} WHERE {lookup} = {key}"
        return self.db_data(query)

    def unit_data(self, unit_id):
        return self.get_details(table_name="unit_master", key=unit_id)

    def product_images(self, product_id):
        data = self.get_details(
            table_name="product_images", key=product_id, lookup="product_id")
        if data.rowcount != 0:
            return [self.IMAGE_PATH + product.image for product in data]
        else:
            return list()

    def categories_data(self, category_id):
        return self.get_details(table_name="categories_master", key=category_id)

    def product_categories(self, product_id):
        return self.get_details(table_name="products_master_category", lookup="products_id", key=product_id)

    def product_ratings(self, product_id):
        return self.get_details(table_name="product_rating", lookup="product_id", key=product_id)

    def favorite_product(self, customer_id):
        query = f"SELECT t1.SKU, t2.id,t2.customer_id,t2.product_id FROM {self.DATABASE_NAME}.products_master t1 inner join {self.DATABASE_NAME}.Favorite_Product t2 on t2.product_id = t1.id where t2.customer_id = {customer_id} ;"
        return self.db_data(query)
