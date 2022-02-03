import shutil
import random
import os
from wayrem_admin.models import Images, Products

# server path = /opt/sftp/wayrem-product-images
# server database = /opt/app/wayrem-admin-backend/media/common_folder


def import_image():
    # path = '/home/suryaaa/Music/image_testing/client-images'
    path = '/opt/app/wayrem-admin-backend/media/wayrem-product-images'

    items = [f for f in os.listdir(
        path) if os.path.isdir(os.path.join(path, f))]

    print(items)

    for i in items:
        print(i)
        product = Products.objects.filter(SKU=i).first()
        if product:
            src_dir = f"{path}/{i}/"
            # dst_dir = f"/home/suryaaa/Music/database/products/{i}/"
            dst_dir = f"/opt/app/wayrem-admin-backend/media/common_folder/products/{i}/"
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            for file_name in os.listdir(src_dir):
                source = src_dir + file_name
                if os.path.isfile(source):
                    isDefault = file_name.split('.')[0]
                    if isDefault == "default":
                        destination = dst_dir + file_name
                        shutil.copy(source, destination)
                        product.primary_image = f"products/{product.SKU}/{file_name}"
                        print("default image copied")
                        product.save()
                    fname = file_name.split('.')[-1]
                    num = random.randint(111, 999)
                    fname = '{}_{}.{}'.format(product.SKU, num, fname)
                    destination = dst_dir + fname
                    if os.path.isfile(source):
                        shutil.copy(source, destination)
                        img = Images()
                        img.product = product
                        img.image = f"products/{product.SKU}/{fname}"
                        img.save()
                        print('copied', file_name)
            shutil.rmtree(src_dir)
        else:
            src_dir = f"{path}/{i}/"
            # dst_dir = f"/home/suryaaa/Music/image_testing/failed"
            dst_dir = f"/opt/app/wayrem-admin-backend/media/common_folder/failed/{i}/"
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            for file_name in os.listdir(src_dir):
                source = src_dir + file_name
                destination = dst_dir + file_name
                shutil.copy(source, destination)
                print('copied', file_name)
            shutil.rmtree(src_dir)
            print("failed!!")
    print("done")
