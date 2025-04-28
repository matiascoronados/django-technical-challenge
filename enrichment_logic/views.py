from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializer import CategorySerializer, MerchantSerializer, KeywordSerializer,InputTransactionSerializer, OutputTransactionSerializer, EnrichmentResponseSerializer
from .models import Category, Merchant, Keyword
import re

# Constantes
STOP_WORDS = frozenset({'y','and','the', 'e', 'o', 'u', 'de', 'del', 'la', 'lo', 'las', 'los', 'en', 'el', 'para', 'por', 'con', 'a', '&'})
CACHE_KEY = 'enrichment_data_processed_v1'

@extend_schema(tags=['Category'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@extend_schema(tags=['Merchant'])
class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

@extend_schema(tags=['Keywords'])
class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

# Esta funcion se encarga de normalizar el texto.
def normalize_text(text):
    if not text: return ""
    text = str(text).lower()
    # Reemplazar simbolos comunes con espacio.
    text = re.sub(r'[*/\-.,\'#\[\]|()!?¿¡]', ' ', text)
    # Quitar espacios adicionales.
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Esta funcion se encarga de crear el patron de busqueda Regex para las keywords.
def get_pattern(keyword_words, keyword_original):
    pattern = None
    try:
        # Crear el patron de busqueda Regex, tanto para el caso de una sola palabra como para el caso que esta se componga por varias palabras.
        if len(keyword_words) == 1:
            pattern = re.compile(rf"\b{re.escape(keyword_words[0])}\b", re.IGNORECASE)
        else:
            pattern_parts = [rf"\b{re.escape(word)}\b" for word in keyword_words]
            pattern = re.compile(r".*?".join(pattern_parts), re.IGNORECASE)

    except re.error:
        print(f"Error regex para el keyword: {keyword_original}")
    return pattern

# Esta funcion se encarga de obtener los datos pre-procesados desde la base de datos o desde la cache.
def get_processed_enrichment_data():
    
    # Intentar obtener datos pre-procesados desde la cache.
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        return cached_data

    # Se obtienen todos los objetos de la base de datos.
    keywords = Keyword.objects.select_related('merchant', 'merchant__category').all()
    merchants = Merchant.objects.select_related('category').all()
    categories = Category.objects.all()

    # Se almacenan los datos pre-procesados en un diccionario, en donde cada clave es un tipo de dato (keywords, comercio, categoria).
    # Cada clave tiene un valor que es otro diccionario, donde las claves 'income' y 'expense' diferencian los tipos de movimiento asociados a cada dato.
    # Observacion: Se asume que todos los comercios tienen una categoria asociada, y que todas las categorias tienen necesariamente un tipo de movimiento.
    processed_data = {
        'keywords': {'income': [], 'expense': []},
        'merchants': {'income': [], 'expense': []},
        'categories': {'income': [], 'expense': []}
    }

    # Pre-procesar Keywords
    for keyword in keywords:
        # Se valida que el comercio y la categoria no sean nulos.
        if not keyword.merchant or not keyword.merchant.category: continue
        # Se valida que la categoria tenga un tipo de movimiento valido.
        category_type = keyword.merchant.category.type
        if category_type not in ['income', 'expense']: continue
        # Se valida que el keyword no sea nulo para luego normalizarlo.
        keyword_original = keyword.keyword
        keyword_normalized = normalize_text(keyword_original)
        if not keyword_normalized: continue

        keyword_words = keyword_normalized.split()
        if not keyword_words: continue
        
        pattern = get_pattern(keyword_words, keyword_original)
        
        if pattern:
            processed_data['keywords'][category_type].append((keyword, pattern, len(keyword_original)))

    # Pre-procesar Merchants
    for merchant in merchants:
        # Se valida la categoria no sea nulo.
        if not merchant.category: continue
        # Se valida que la categoria tenga un tipo de movimiento valido.
        category_type = merchant.category.type
        if category_type not in ['income', 'expense']: continue
        # Se valida que el nombre del comercio no sea nulo para luego normalizarlo.
        merchant_original = merchant.merchant_name
        merchant_normalized = normalize_text(merchant_original)
        if not merchant_normalized: continue

        merchant_words = merchant_normalized.split()
        if not merchant_words: continue

        pattern = get_pattern(merchant_words, merchant_original)

        if pattern:
            processed_data['merchants'][category_type].append((merchant, pattern, len(merchant_original)))

    # Pre-procesar Categories
    for category in categories:
        category_type = category.type
        # Se valida que la categoria tenga un tipo de movimiento valido.
        if category_type not in ['income', 'expense']: continue
        category_normalized = normalize_text(category.name)
        
        # Crear el set de palabras de la categoria (excluyendo stop words)
        category_words_set = {word for word in category_normalized.split() if word and word not in STOP_WORDS}
        if not category_words_set: continue

        # Guardar objeto y set de palabras precalculado
        processed_data['categories'][category_type].append((category, category_words_set))

    # Ordenar keywords y merchants por longitud, con la finalidad de encontrar primero el mas largo.
    for type in ['income', 'expense']:
        processed_data['keywords'][type].sort(key=lambda x: x[2], reverse=True)
        processed_data['merchants'][type].sort(key=lambda x: x[2], reverse=True)

    # Guardar en cache los datos pre-procesados
    cache.set(CACHE_KEY, processed_data, timeout=3600)
    return processed_data


class EnrichTransactionsAPIView(APIView):
    @extend_schema(
        request=InputTransactionSerializer(many=True),
        responses={
            200: EnrichmentResponseSerializer,
        },
        tags=['Enrichment']
    )
    def post(self, request, *args, **kwargs):
        # Validación de entrada
        input_serializer = InputTransactionSerializer(data=request.data, many=True)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transactions = input_serializer.validated_data
        total_transactions = len(transactions)
        if total_transactions == 0:
             return Response({"transactions": [], "metrics": {"total_transactions": 0, "categorization_rate": 0, "merchant_identification_rate": 0}}, status=status.HTTP_200_OK)

        # Obtener datos pre-procesados
        processed_data = get_processed_enrichment_data()

        results = []
        categorized_match_count = 0
        merchant_match_count = 0

        for transaction in transactions:
            # Se procesan los datos de la transaccion.
            description_original = transaction['description']
            description_normalized = normalize_text(description_original)
            amount = transaction['amount']
            target_category_type = 'income' if amount >= 0 else 'expense'

            # Se inicializan las variables para almacenar los resultados de la busqueda.
            found_merchant = None
            found_category = None
            match_found = False

            # Para todas las busquedas se filtra primero por el tipo de movimiento (ingreso o gasto) de la transaccion.
            
            # Se utiliza regex para buscar la exixtencia del patron de los keywords en la descripcion de la transaccion.
            for keyword, pattern, _ in processed_data['keywords'][target_category_type]:
                if pattern.search(description_normalized):
                    found_merchant = keyword.merchant
                    found_category = found_merchant.category
                    match_found = True
                    break

            # Se utiliza regex para buscar la existencia del patron de los nombres del comercios en la descripcion de la transaccion.
            if not match_found:
                for merchant, pattern, _ in processed_data['merchants'][target_category_type]:
                    if pattern.search(description_normalized):
                        found_merchant = merchant
                        found_category = merchant.category
                        match_found = True
                        break

            # Se comprueba si alguna de las palabras que forman el nombre de una categoria existen dentro de la descripcion de la transaccion.
            if not match_found:
                best_category_match_score = 0
                matched_category = None
                # Se obtiene el set de palabras de la descripcion de la transaccion (excluyendo stop words)
                description_words_set = {word for word in description_normalized.split() if word and word not in STOP_WORDS}
                
                if description_words_set:
                    for category, category_words_set in processed_data['categories'][target_category_type]:
                        # Se verifica si la categoria tiene palabras que coincidan con las de la descripcion de la transaccion.
                        common_words = description_words_set.intersection(category_words_set)
                        # Se calcula un puntaje basado en la cantidad de palabras coincidentes.
                        score = len(common_words)
                        # Se verifica si el puntaje es mayor al mejor puntaje encontrado hasta ahora.
                        if score > best_category_match_score:
                            best_category_match_score = score
                            matched_category = category

                if matched_category:
                    found_category = matched_category
                    found_merchant = None
                    match_found = True

            if found_category: categorized_match_count += 1
            if found_merchant: merchant_match_count += 1
            # Se conforma el diccionario de salida con los datos encontrados para la trasanccion.
            output_trans_dict = {
                'description': description_original,
                'amount': amount,
                'date': transaction['date'],
                'enriched_category': found_category,
                'enriched_merchant': found_merchant
            }
            results.append(output_trans_dict)

        # Calculo de Metricas
        categorization_rate = (categorized_match_count / total_transactions * 100) if total_transactions > 0 else 0
        merchant_identification_rate = (merchant_match_count / total_transactions * 100) if total_transactions > 0 else 0

        metrics = {
            "total_transactions": total_transactions,
            "categorization_rate": round(categorization_rate, 2),
            "merchant_identification_rate": round(merchant_identification_rate, 2),
        }

        output_serializer = OutputTransactionSerializer(results, many=True)

        response_data = {
            "transactions": output_serializer.data,
            "metrics": metrics
        }

        return Response(response_data, status=status.HTTP_200_OK)