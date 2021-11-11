from django.urls import path
from wayrem_admin import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users-registration/',
         views.user_signup, name='sub-admin-register'),
    path('forgot-password/', views.Forgot_Password.as_view(), name='forgot-password'),
    path('change-password/', views.Change_PasswordView.as_view(),
         name='change-password'),
    path('reset-password/', views.Reset_Password.as_view(), name='reset-password'),
    path('deleteuser/', views.DeleteUser.as_view(), name='deleteuser'),
    path('activeblock/<str:id>/',
         views.Active_BlockUser.as_view(), name='activeblock'),
    path('users-list/', views.UsersList.as_view(), name='userlist'),
    path('update_profile/', views.update_profile, name='updateprofile'),
    path('createcategory/', views.create_category, name='createcategory'),
    path('categories-list/', views.CategoriesList.as_view(), name='categorieslist'),
    path('delete-categories/', views.DeleteCategories.as_view(),
         name='deletecategories'),
    path('update-categories/<str:id>/',
         views.update_categories, name='updatecategory'),
    #     path('create-product/', views.create_product, name='product'),
    path('product-list/', views.ProductList.as_view(), name='productlist'),
    #     path('delete-product/', views.DeleteProduct.as_view(), name='deleteproduct'),
    #     path('update-product/<str:id>/', views.update_product, name='updateproduct'),
    path('supplier-registration/', views.supplier_register, name='suppregister'),
    path('supplier-list/', views.SupplierList.as_view(), name='supplierlist'),
    path('delete-supplier/', views.DeleteSupplier.as_view(), name='deletesupplier'),
    path('activeblock-supplier/<str:id>/',
         views.Active_BlockSupplier.as_view(), name='activeblocksupplier'),
    path('product-view-one/', views.product_view_one, name='productviewone'),
    path('product-view-two/', views.product_view_two, name='productviewtwo'),
    path('product-view-three/', views.product_view_three, name='productviewthree'),
    path('product-view-four/', views.product_view_four, name='productviewfour'),
    path('create-ingredients/', views.create_ingredients, name='createingredients'),
    path('ingredients-list/', views.ingredientsList,
         name='ingredientslist'),
    path('delete-ingredients/', views.DeleteIngredients.as_view(),
         name='deleteingredients'),
    path('update-ingredients/<str:id>/',
         views.update_ingredients, name='updateingredients'),
    path('create-po/', views.create_po1, name='createpo'),
    #     path('create-po2/', views.create_po2, name='createpo2'),
    path('update-product/<str:id>/', views.update_product, name='updateproduct'),
    path('delete-product/', views.DeleteProduct.as_view(),
         name='deleteproduct'),
    #     path('create-po2/', views.create_po2, name='createpo2'),
    path('supplier-details/<str:id>/',
         views.supplier_details, name='supplierdetails'),
    path('user-details/<str:id>/', views.user_details, name='userdetails'),
    path('category-details/<str:id>/',
         views.category_details, name='categorydetails'),
    path('product-details/<str:id>', views.product_details, name='productdetails'),



    #   Roles CRUD urls start-------------------------

    path('roles/list/', views.rolesList, name='roles_list'),
    path('roles/create/', views.createRoles, name='roles_create'),
    path('roles/update/', views.cupdateRoles, name='roles_update'),
    path('roles/view/', views.viewRoles, name='roles_view'),
    path('roles/activeUnactive/', views.activeUnactiveRoles,
         name='roles_active_unactive'),

    #   Roles CRUD urls end-------------------------

    path('inputBar/', views.inputBar, name='inputBar'),
    path('product/', views.product, name='product'),
    path('pdf_user/', views.pdf_userlist, name='userpdf'),
    path('pdf_supplier/', views.pdf_supplier, name='supplierpdf'),
    path('pdf_product/', views.pdf_product, name='productpdf'),
    path('pdf_category/', views.pdf_category, name='categorypdf'),
    # ---------------Excel -----------------------
    path('excel_user/', views.user_excel, name='exceluser'),
    path('excel_supplier/', views.supplier_excel, name='excelsupplier'),
    path('excel_po/', views.po_excel, name='excelpo'),
    path('excel_product/', views.product_excel, name='excelproduct'),
    path('excel_ingredient/', views.ingredient_excel, name='excelingredient'),
    # ---------------Excel Ends ----------------
    #     ajax
    path('ajax/load-supplier/', views.load_supplier, name='ajax_load_supplier'),

    path('purchase_order/', views.create_purchase_order, name='create_po'),
    path('po-list/', views.POList.as_view(), name='polist'),
    path('import-ingredients/', views.import_ingredients, name="importingredients"),
    path('update-user/<str:id>/',
         views.update_user, name='updateuser'),
    path('update-supplier/<str:id>/',
         views.update_supplier, name='updatesupplier'),
    path('view-po/<str:id>', views.viewpo, name='viewpo'),
    path('edit-po/<str:id>', views.editpo, name='editpo'),
    path('edit-po-status/<str:id>', views.statuspo, name='po_status'),
    path('delete-po/', views.DeletePO.as_view(),
         name='deletepo'),
    path('status-po/', views.POStatus.as_view(),
         name='statuspo'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
