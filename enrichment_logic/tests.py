from django.test import TestCase
from django.core.cache import cache
from .models import Category, Merchant, Keyword
import json
import uuid
import random
import time

class CategoryViewSetTestCase(TestCase):
    @classmethod
    # Metodo de creacion de datos de prueba.
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(name='Gasto Test', type='expense')
        cls.category2 = Category.objects.create(name='Ingreso Test', type='income')
        cls.list_url = '/api/v1/categories/'
        cls.detail_url = lambda pk: f'/api/v1/categories/{pk}/'
        cache.clear()
        print("\nCategory Test")

    # Test para probar el listado de categorías
    def test_list_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(item['name'] == self.category1.name for item in results))
        self.assertTrue(any(item['name'] == self.category2.name for item in results))

    # Test para crear una categoría con datos válidos
    def test_create_category_success(self):
        payload = {'name': 'Nueva Categoria Gasto', 'type': 'expense'}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Nueva Categoria Gasto')
        new_cat_pk_str = data.get('id')
        self.assertIsNotNone(new_cat_pk_str)
        self.assertTrue(Category.objects.filter(pk=uuid.UUID(new_cat_pk_str)).exists())

    # Test para crear una categoría sin tipo.
    def test_create_category_invalid_data(self):
        payload = {'name': 'Falta tipo'}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Test para crear una categoría con un nombre ya existente.
    def test_retrieve_category_success(self):
        response = self.client.get(self.detail_url(self.category1.pk))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], str(self.category1.pk))
        self.assertEqual(data['name'], self.category1.name)

    # Test para obtener una categoría que no existe.
    def test_retrieve_category_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.get(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)

    # Test para actualizar una categoría con PUT
    def test_update_category_put_success(self):
        payload = {'name': 'Gasto Actualizado PUT', 'type': 'expense'}
        response = self.client.put(self.detail_url(self.category1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Gasto Actualizado PUT')
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, 'Gasto Actualizado PUT')

    # Test para actualizar una categoría con PATCH
    def test_update_category_patch_success(self):
        payload = {'name': 'Gasto Actualizado PATCH'}
        response = self.client.patch(self.detail_url(self.category1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Gasto Actualizado PATCH')
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, 'Gasto Actualizado PATCH')
        self.assertEqual(self.category1.type, 'expense')

    # Test para actualizar una categoría que no existe.
    def test_update_category_not_found(self):
        payload = {'name': 'No importa'}
        non_existent_pk = uuid.uuid4()
        response_put = self.client.put(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        response_patch = self.client.patch(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response_put.status_code, 404)
        self.assertEqual(response_patch.status_code, 404)

    # Test para eliminar una categoría que existe.
    def test_delete_category_success(self):
        response = self.client.delete(self.detail_url(self.category1.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(pk=self.category1.pk).exists())

    # Test para eliminar una categoría que no existe.
    def test_delete_category_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.delete(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)


class MerchantViewSetTestCase(TestCase):
    @classmethod
    # Metodo de creacion de datos de prueba.
    def setUpTestData(cls):
        cls.cat_for_merchant = Category.objects.create(name='Empresa Gasto Test', type='expense')
        cls.merchant1 = Merchant.objects.create(merchant_name='Comercio Uno Test', category=cls.cat_for_merchant)
        cls.merchant2 = Merchant.objects.create(merchant_name='Comercio Dos Test', category=cls.cat_for_merchant)
        cls.list_url = '/api/v1/merchant/'
        cls.detail_url = lambda pk: f'/api/v1/merchant/{pk}/'
        cache.clear()
        print("\nMerchant Test")

    # Test para probar el listado de comercios
    def test_list_merchants(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(item['merchant_name'] == self.merchant1.merchant_name for item in results))

    # Test para crear un comercio con datos válidos
    def test_create_merchant_success(self):
        payload = {'merchant_name': 'Nuevo Comercio Test', 'category': str(self.cat_for_merchant.id)}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['merchant_name'], 'Nuevo Comercio Test')
        self.assertEqual(data['category'], str(self.cat_for_merchant.id))
        new_merch_pk_str = data.get('id')
        self.assertIsNotNone(new_merch_pk_str)
        self.assertTrue(Merchant.objects.filter(pk=uuid.UUID(new_merch_pk_str)).exists())

    # Test para crear un comercio sin categoría.
    def test_create_merchant_without_category_success(self):
        payload = {'merchant_name': 'Comercio Sin Categoria'}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['merchant_name'], 'Comercio Sin Categoria')
        self.assertIsNone(data['category'])
        merchant_in_db = Merchant.objects.get(merchant_name='Comercio Sin Categoria')
        self.assertIsNone(merchant_in_db.category)

    # Test para crear un comercio con un nombre ya existente.
    def test_retrieve_merchant_success(self):
        response = self.client.get(self.detail_url(self.merchant1.pk))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], str(self.merchant1.pk))
        self.assertEqual(data['merchant_name'], self.merchant1.merchant_name)
        self.assertEqual(data['category'], str(self.cat_for_merchant.id))

    # Test para obtener un comercio que no existe.
    def test_retrieve_merchant_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.get(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)

    # Test para actualizar un comercio con PUT
    def test_update_merchant_put_success(self):
        cat_new = Category.objects.create(name='Otro Comercio Gasto', type='expense')
        payload = {'merchant_name': 'Comercio Actualizado PUT', 'category': str(cat_new.id)}
        response = self.client.put(self.detail_url(self.merchant1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['merchant_name'], 'Comercio Actualizado PUT')
        self.assertEqual(data['category'], str(cat_new.id))
        self.merchant1.refresh_from_db()
        self.assertEqual(self.merchant1.merchant_name, 'Comercio Actualizado PUT')
        self.assertEqual(self.merchant1.category.id, cat_new.id)

    # Test para actualizar un comercio con PATCH
    def test_update_merchant_patch_success(self):
        payload = {'merchant_name': 'Comercio Actualizado PATCH'}
        response = self.client.patch(self.detail_url(self.merchant1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['merchant_name'], 'Comercio Actualizado PATCH')
        self.merchant1.refresh_from_db()
        self.assertEqual(self.merchant1.merchant_name, 'Comercio Actualizado PATCH')
        self.assertEqual(self.merchant1.category.id, self.cat_for_merchant.id)

    # Test para actualizar un comercio que no existe.
    def test_update_merchant_not_found(self):
        payload = {'merchant_name': 'No importa'}
        non_existent_pk = uuid.uuid4()
        response_put = self.client.put(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        response_patch = self.client.patch(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response_put.status_code, 404)
        self.assertEqual(response_patch.status_code, 404)

    # Test para eliminar un comercio que existe.
    def test_delete_merchant_success(self):
        response = self.client.delete(self.detail_url(self.merchant1.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Merchant.objects.filter(pk=self.merchant1.pk).exists())

    # Test para eliminar un comercio que no existe.
    def test_delete_merchant_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.delete(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)


class KeywordViewSetTestCase(TestCase):
    @classmethod
    # Metodo de creacion de datos de prueba.
    def setUpTestData(cls):
        cat = Category.objects.create(name='Gasto Keyword Test', type='expense')
        cls.merch_for_kw = Merchant.objects.create(merchant_name='Comercio Keyword Test', category=cat)
        cls.keyword1 = Keyword.objects.create(keyword='Keyword Uno Test', merchant=cls.merch_for_kw)
        cls.keyword2 = Keyword.objects.create(keyword='Keyword Dos Test', merchant=cls.merch_for_kw)
        cls.list_url = '/api/v1/keyword/'
        cls.detail_url = lambda pk: f'/api/v1/keyword/{pk}/'
        cache.clear()
        print("\nKeyword Test")

    # Test para probar el listado de keywords
    def test_list_keywords(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(item['keyword'] == self.keyword1.keyword for item in results))

    # Test para crear una keyword con datos válidos
    def test_create_keyword_success(self):
        payload = {'keyword': 'Nueva Keyword Test', 'merchant': str(self.merch_for_kw.id)}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['keyword'], 'Nueva Keyword Test')
        self.assertEqual(data['merchant'], str(self.merch_for_kw.id))
        new_kw_pk_str = data.get('id')
        self.assertIsNotNone(new_kw_pk_str)
        self.assertTrue(Keyword.objects.filter(pk=uuid.UUID(new_kw_pk_str)).exists())

    # Test para crear una keyword sin comercio.
    def test_create_keyword_without_merchant_success(self):
        payload = {'keyword': 'Keyword Sin Merchant'}
        response = self.client.post(self.list_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['keyword'], 'Keyword Sin Merchant')
        self.assertIsNone(data['merchant'])
        keyword_in_db = Keyword.objects.get(keyword='Keyword Sin Merchant')
        self.assertIsNone(keyword_in_db.merchant)

    # Test para crear una keyword con un nombre ya existente.
    def test_retrieve_keyword_success(self):
        response = self.client.get(self.detail_url(self.keyword1.pk))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], str(self.keyword1.pk))
        self.assertEqual(data['keyword'], self.keyword1.keyword)
        self.assertEqual(data['merchant'], str(self.merch_for_kw.id))

    # Test para obtener una keyword que no existe.
    def test_retrieve_keyword_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.get(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)

    # Test para actualizar una keyword con PUT
    def test_update_keyword_put_success(self):
        cat_new = Category.objects.create(name='Cat Nueva KW', type='expense')
        merch_new = Merchant.objects.create(merchant_name='Merch Nuevo KW', category=cat_new)
        payload = {'keyword': 'KW Actualizada PUT', 'merchant': str(merch_new.id)}
        response = self.client.put(self.detail_url(self.keyword1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['keyword'], 'KW Actualizada PUT')
        self.assertEqual(data['merchant'], str(merch_new.id))
        self.keyword1.refresh_from_db()
        self.assertEqual(self.keyword1.keyword, 'KW Actualizada PUT')
        self.assertEqual(self.keyword1.merchant.id, merch_new.id)

    # Test para actualizar una keyword con PATCH
    def test_update_keyword_patch_success(self):
        payload = {'keyword': 'KW Actualizada PATCH'}
        response = self.client.patch(self.detail_url(self.keyword1.pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['keyword'], 'KW Actualizada PATCH')
        self.keyword1.refresh_from_db()
        self.assertEqual(self.keyword1.keyword, 'KW Actualizada PATCH')
        self.assertEqual(self.keyword1.merchant.id, self.merch_for_kw.id)

    # Test para actualizar una keyword que no existe.
    def test_update_keyword_not_found(self):
        payload = {'keyword': 'No importa'}
        non_existent_pk = uuid.uuid4()
        response_put = self.client.put(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        response_patch = self.client.patch(self.detail_url(non_existent_pk), json.dumps(payload), content_type='application/json')
        self.assertEqual(response_put.status_code, 404)
        self.assertEqual(response_patch.status_code, 404)

    # Test para eliminar una keyword que existe.
    def test_delete_keyword_success(self):
        response = self.client.delete(self.detail_url(self.keyword1.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Keyword.objects.filter(pk=self.keyword1.pk).exists())

    # Test para eliminar una keyword que no existe.
    def test_delete_keyword_not_found(self):
        non_existent_pk = uuid.uuid4()
        response = self.client.delete(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, 404)
        
class EnrichTransactionsAPIViewTestCase(TestCase):
    @classmethod
    # Metodo de creacion de datos de prueba.
    def setUpTestData(cls):
        # Categorias
        cls.cat_sueldo = Category.objects.create(name='Sueldo Enr', type='income')
        cls.cat_transporte = Category.objects.create(name='Transporte Enr', type='expense')
        cls.cat_supermercado = Category.objects.create(name='Supermercado Enr', type='expense')
        cls.cat_comida = Category.objects.create(name='Comida Enr', type='expense')
        cls.cat_otros_gastos = Category.objects.create(name='Otros Gastos Enr', type='expense')
        cls.cat_servicios = Category.objects.create(name='Servicios Basicos Enr', type='expense')

        # Comercios
        cls.merch_uber = Merchant.objects.create(merchant_name='Uber Enr', category=cls.cat_transporte)
        cls.merch_lider = Merchant.objects.create(merchant_name='Lider', category=cls.cat_supermercado)
        cls.merch_falabella = Merchant.objects.create(merchant_name='Falabella Enr', category=cls.cat_otros_gastos)
        cls.merch_enel = Merchant.objects.create(merchant_name='Enel Enr', category=cls.cat_servicios)
        cls.merch_empresa_x = Merchant.objects.create(merchant_name='Empresa X Enr', category=cls.cat_sueldo)

        # Keywords
        Keyword.objects.create(keyword='Uber', merchant=cls.merch_uber)
        Keyword.objects.create(keyword='Uber Eats', merchant=cls.merch_uber)
        Keyword.objects.create(keyword='Luz Enel', merchant=cls.merch_enel)
        Keyword.objects.create(keyword='pago sol', merchant=cls.merch_lider)
        Keyword.objects.create(keyword='Falabella Viajes', merchant=cls.merch_falabella)
        Keyword.objects.create(keyword='Sueldo Empresa X', merchant=cls.merch_empresa_x)

        cls.enrich_url = '/api/v1/transactions/enrich/'

        cache.clear()
        print("\nEnrichment Test")
        
    # Test para probar el match exitoso por Keyword.
    def test_success_keyword_match_expense(self):
        payload = [{"description": "Viaje en Uber Santiago", "amount": -4500, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['total_transactions'], 1)
        self.assertEqual(data['metrics']['categorization_rate'], 100.0)
        self.assertEqual(data['metrics']['merchant_identification_rate'], 100.0)
        tx = data['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_transporte.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_uber.id))

    # Test para probar el match exitoso por nombre de comercio.
    def test_success_merchant_match_expense(self):
        payload = [{"description": "Compra en Lider Vitacura", "amount": -15200, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['categorization_rate'], 100.0)
        self.assertEqual(data['metrics']['merchant_identification_rate'], 100.0)
        tx = data['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_supermercado.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_lider.id))

    # Test para probar el match exitoso por nombre de categoría.
    def test_success_category_match_expense(self):
        payload = [{"description": "Gastos supermercado varios", "amount": -8750, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['categorization_rate'], 100.0)
        self.assertEqual(data['metrics']['merchant_identification_rate'], 0.0)
        tx = data['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNone(tx.get('enriched_merchant'), "Merchant should be None for category-only match")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_supermercado.id))

    # Test para probar el match exitoso para el caso de una transaccion de ingreso.
    def test_success_income_match(self):
        payload = [{"description": "Abono Sueldo Empresa X Ltda", "amount": 850000, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['categorization_rate'], 100.0)
        tx = data['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_sueldo.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_empresa_x.id))

    # Test para probar un match fallido.
    def test_no_match(self):
        payload = [{"description": "Alguna cosa rara xyz", "amount": -1000, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['categorization_rate'], 0.0)
        self.assertEqual(data['metrics']['merchant_identification_rate'], 0.0)
        tx = data['transactions'][0]
        self.assertIsNone(tx.get('enriched_category'))
        self.assertIsNone(tx.get('enriched_merchant'))

    # Test para probar una lista con varias transacciones con resultados mixtos.
    def test_multiple_transactions_mixed(self):
        payload = [
            {"description": "Viaje Uber", "amount": -5000, "date": "2025-04-28"}, # Match por Keyword
            {"description": "Supermercado mes", "amount": -22000, "date": "2025-04-28"}, # Match por Categoria
            {"description": "Otro gasto", "amount": -3000, "date": "2025-04-28"} # Sin Match
        ]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        data = response.json()
        self.assertEqual(data['metrics']['total_transactions'], 3)
        self.assertAlmostEqual(data['metrics']['categorization_rate'], 66.67, places=2)
        self.assertAlmostEqual(data['metrics']['merchant_identification_rate'], 33.33, places=2)
        tx0, tx1, tx2 = data['transactions']
        self.assertIsNotNone(tx0.get('enriched_category'), "TX0 Category missing")
        self.assertIsNotNone(tx0.get('enriched_merchant'), "TX0 Merchant missing")
        if tx0.get('enriched_category'): self.assertEqual(tx0['enriched_category'].get('id'), str(self.cat_transporte.id))
        if tx0.get('enriched_merchant'): self.assertEqual(tx0['enriched_merchant'].get('id'), str(self.merch_uber.id))
        self.assertIsNotNone(tx1.get('enriched_category'), "TX1 Category missing")
        self.assertIsNone(tx1.get('enriched_merchant'), "TX1 Merchant should be None")
        if tx1.get('enriched_category'): self.assertEqual(tx1['enriched_category'].get('id'), str(self.cat_supermercado.id))
        self.assertIsNone(tx2.get('enriched_category'), "TX2 Category should be None")
        self.assertIsNone(tx2.get('enriched_merchant'), "TX2 Merchant should be None")

    # Test para probar campos invalidos en la entrada.
    def test_error_invalid_input_missing_field(self):
        payload = [{"description": "Falta amount", "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Test para probar cuando se ingresa una transaccion con descripcion vacia.
    def test_error_empty_description(self):
        payload = [{"description": "", "amount": -100, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        try:
            data = response.json()
            self.assertIn('description', data[0])
            self.assertIn('blank', data[0]['description'][0])
        except json.JSONDecodeError:
            self.fail("Response was not valid JSON for 400 error")

    # Test para probar cuando se ingresa una transaccion con descripcion nula.
    def test_error_null_description(self):
        payload = [{"description": None, "amount": -100, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        try:
            data = response.json()
            self.assertIn('description', data[0])
            self.assertIn('null', data[0]['description'][0])
        except json.JSONDecodeError:
            self.fail("Response was not valid JSON for 400 error")

    # Test para probar cuando se ingresa una transaccion con amount igual a 0.
    def test_edge_zero_amount(self):
        payload = [{"description": "Ingreso Sueldo Empresa X", "amount": 0, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        tx = response.json()['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_sueldo.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_empresa_x.id))

    # Test para probar cuando se ingresa una transaccion con una descripcion que contenga caracteres especiales.
    def test_edge_special_chars_normalization(self):
        payload = [{"description": "Pago #Luz / Enel.", "amount": -11500, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        tx = response.json()['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_servicios.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_enel.id))

    # Test para probar cuando se ingresa una transaccion con una descripcion que contenga caracteres mayusculas y minusculas.
    def test_edge_case_insensitivity(self):
        payload = [{"description": "UBER EATS pago", "amount": -6200, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        tx = response.json()['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
            self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_transporte.id))
        if tx.get('enriched_merchant'):
            self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_uber.id))

    # Test para asegurar que se elige la keyword más larga cuando varias keywords coinciden con la misma transacción
    def test_edge_priority_keyword_over_merchant(self):
        payload = [{"description": "Reserva Falabella Viajes sky", "amount": -150000, "date": "2025-04-28"}]
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content}")
        tx = response.json()['transactions'][0]
        self.assertIsNotNone(tx.get('enriched_category'), "Category should not be None")
        self.assertIsNotNone(tx.get('enriched_merchant'), "Merchant should not be None")
        if tx.get('enriched_category'):
             self.assertEqual(tx['enriched_category'].get('id'), str(self.cat_otros_gastos.id))
        if tx.get('enriched_merchant'):
             self.assertEqual(tx['enriched_merchant'].get('id'), str(self.merch_falabella.id))

    # Test para verificar que se maneja correctamente una gran cantidad de transacciones (1000 registros).
    def test_large_volume_enrichment(self):
        print("\nStarting large transactions test (1000 records)...")
        num_records = 1000
        payload = []
        base_date = "2025-04-28"
        description_options = [
            f"Compra Uber",
            f"Pago Luz Enel",
            f"Gasto Supermercado Lider",
            f"Ingreso Sueldo Empresa",
            f"Falabella Viajes Reserva"
        ]

        for _ in range(num_records):
            amount = random.randint(-50000, 20000)
            description = random.choice(description_options)
            payload.append({
                "description": description,
                "amount": amount,
                "date": base_date
            })
            
        start_time = time.time()
        response = self.client.post(self.enrich_url, json.dumps(payload), content_type='application/json')
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Test completed in {duration:.4f} seconds.")

        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}. Response: {response.content[:500]}...")
        data = response.json()

        self.assertIn('metrics', data)
        self.assertIn('transactions', data)
        self.assertEqual(data['metrics'].get('total_transactions'), num_records)
        self.assertEqual(len(data['transactions']), num_records)
    
        max_duration = 8.0
        self.assertLess(duration, max_duration, f"Processing {num_records} records took {duration:.4f}s, exceeding the limit of {max_duration}s.")