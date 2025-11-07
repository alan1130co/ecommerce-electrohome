from django.db.models import Count, Q, Avg, F, Sum
from django.conf import settings
from django.core.cache import cache
from django.db import models
from datetime import timedelta
from django.utils import timezone

class RecommendationEngine:
    """
    Recommendation Engine for ElectroHome
    Versión mejorada con mejor manejo de caché y scoring
    """
    
    def __init__(self, user=None, session_key=None):
        self.user = user
        self.session_key = session_key
        self.cache_timeout = getattr(settings, 'RECOMMENDATION_CACHE_TIMEOUT', 3600)
    
    # ========== CONTENT-BASED RECOMMENDATIONS ==========
    
    def get_similar_products(self, product, limit=6):
        """Similar products based on category"""
        from .models import Producto
        
        cache_key = f'similar_products_{product.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        similar = Producto.objects.filter(
            categoria=product.categoria,
            activo=True,
            stock__gt=0
        ).exclude(
            id=product.id
        ).select_related('categoria').order_by('-fecha_creacion')[:limit]
        
        similar = list(similar)
        cache.set(cache_key, similar, self.cache_timeout)
        
        return similar
    
    def get_frequently_bought_together(self, product, limit=4):
        """Products frequently bought together"""
        from .models import Purchase, Producto
        
        cache_key = f'bought_together_{product.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        users_who_bought = Purchase.objects.filter(
            product=product
        ).values_list('user_id', flat=True).distinct()
        
        if not users_who_bought:
            return []
        
        other_products = Purchase.objects.filter(
            user_id__in=users_who_bought
        ).exclude(
            product=product
        ).values('product').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        product_ids_ordered = [item['product'] for item in other_products]
        
        if not product_ids_ordered:
            return []
        
        products_dict = {
            p.id: p for p in Producto.objects.filter(
                id__in=product_ids_ordered, 
                activo=True,
                stock__gt=0
            ).select_related('categoria')
        }
        
        products = [products_dict[pid] for pid in product_ids_ordered if pid in products_dict]
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    # ========== USER RECOMMENDATIONS ==========
    
    def get_personalized_recommendations(self, limit=10):
        """
        Personalized recommendations based on user history
        MEJORADO: No excluye productos vistos, solo comprados
        """
        if not self.user:
            return self.get_popular_products(limit)
        
        cache_key = f'personalized_recs_{self.user.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import ProductView, Purchase, Producto
        
        recommendations = []
        seen_ids = set()
        
        # 1. Basado en productos vistos recientemente (50%)
        recent_views = ProductView.objects.filter(
            user=self.user
        ).select_related('product__categoria').order_by('-viewed_at')[:20]
        
        recent_categories = list(set(
            view.product.categoria_id for view in recent_views if view.product.categoria_id
        ))
        
        if recent_categories:
            # Solo excluir productos comprados, NO vistos
            purchased_ids = Purchase.objects.filter(
                user=self.user
            ).values_list('product_id', flat=True)
            
            category_products = Producto.objects.filter(
                categoria_id__in=recent_categories,
                activo=True,
                stock__gt=0
            ).exclude(
                id__in=purchased_ids
            ).select_related('categoria').order_by('-fecha_creacion')[:int(limit * 0.5)]
            
            for product in category_products:
                if product.id not in seen_ids:
                    recommendations.append(product)
                    seen_ids.add(product.id)
        
        # 2. Basado en compras pasadas (30%)
        past_purchases_categories = Purchase.objects.filter(
            user=self.user
        ).values_list('product__categoria', flat=True).distinct()
        
        if past_purchases_categories:
            purchased_ids = Purchase.objects.filter(
                user=self.user
            ).values_list('product_id', flat=True)
            
            similar_to_purchased = Producto.objects.filter(
                categoria__in=past_purchases_categories,
                activo=True,
                stock__gt=0
            ).exclude(
                Q(id__in=purchased_ids) | Q(id__in=seen_ids)
            ).select_related('categoria').order_by('-fecha_creacion')[:int(limit * 0.3)]
            
            for product in similar_to_purchased:
                if product.id not in seen_ids:
                    recommendations.append(product)
                    seen_ids.add(product.id)
        
        # 3. Llenar con productos populares (20%)
        if len(recommendations) < limit:
            remaining = limit - len(recommendations)
            popular = self.get_popular_products(remaining + 5)
            
            for product in popular:
                if product.id not in seen_ids and len(recommendations) < limit:
                    recommendations.append(product)
                    seen_ids.add(product.id)
        
        recommendations = recommendations[:limit]
        cache.set(cache_key, recommendations, self.cache_timeout // 2)
        
        return recommendations
    
    def get_collaborative_recommendations(self, limit=10):
        """Collaborative filtering: "Users like you also viewed" """
        if not self.user:
            return []
        
        cache_key = f'collaborative_recs_{self.user.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import ProductView, Producto
        
        user_viewed = set(
            ProductView.objects.filter(
                user=self.user
            ).values_list('product_id', flat=True)
        )
        
        if not user_viewed:
            return []
        
        similar_users = ProductView.objects.filter(
            product_id__in=user_viewed
        ).exclude(
            user=self.user
        ).values('user_id').annotate(
            common_views=Count('id')
        ).order_by('-common_views')[:20].values_list('user_id', flat=True)
        
        if not similar_users:
            return []
        
        recommended = ProductView.objects.filter(
            user_id__in=similar_users
        ).exclude(
            product_id__in=user_viewed
        ).values('product_id').annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:limit]
        
        product_ids_ordered = [item['product_id'] for item in recommended]
        
        if not product_ids_ordered:
            return []
        
        products_dict = {
            p.id: p for p in Producto.objects.filter(
                id__in=product_ids_ordered,
                activo=True,
                stock__gt=0
            ).select_related('categoria')
        }
        
        products = [products_dict[pid] for pid in product_ids_ordered if pid in products_dict]
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    # ========== GENERAL RECOMMENDATIONS ==========
    
    def get_popular_products(self, limit=10):
        """Most popular products (most viewed in last 30 days)"""
        from .models import ProductView, Producto
        
        cache_key = f'popular_products_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        since = timezone.now() - timedelta(days=30)
        
        popular_ids = ProductView.objects.filter(
            viewed_at__gte=since
        ).values('product_id').annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:limit].values_list('product_id', flat=True)
        
        products_dict = {
            p.id: p for p in Producto.objects.filter(
                id__in=popular_ids,
                activo=True,
                stock__gt=0
            ).select_related('categoria')
        }
        
        products = [products_dict[pid] for pid in popular_ids if pid in products_dict]
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    def get_trending_products(self, days=7, limit=10):
        """Trending products (most viewed in last X days)"""
        from .models import ProductView, Producto
        
        cache_key = f'trending_products_{days}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        since = timezone.now() - timedelta(days=days)
        
        trending_ids = ProductView.objects.filter(
            viewed_at__gte=since
        ).values('product_id').annotate(
            view_count=Count('id')
        ).filter(
            view_count__gte=3
        ).order_by('-view_count')[:limit].values_list('product_id', flat=True)
        
        products_dict = {
            p.id: p for p in Producto.objects.filter(
                id__in=trending_ids,
                activo=True,
                stock__gt=0
            ).select_related('categoria')
        }
        
        products = [products_dict[pid] for pid in trending_ids if pid in products_dict]
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    def get_best_rated_products(self, limit=10):
        """Best rated products with Bayesian average"""
        from .models import ProductRating, Producto
        
        cache_key = f'best_rated_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        MIN_RATINGS = 3
        GLOBAL_AVG = 3.5
        
        best_rated = ProductRating.objects.values('product_id').annotate(
            avg_rating=Avg('rating'),
            rating_count=Count('id')
        ).filter(
            rating_count__gte=MIN_RATINGS
        )
        
        rated_products = []
        for item in best_rated:
            v = item['rating_count']
            R = item['avg_rating']
            weighted_rating = (v / (v + MIN_RATINGS)) * R + (MIN_RATINGS / (v + MIN_RATINGS)) * GLOBAL_AVG
            rated_products.append({
                'product_id': item['product_id'],
                'weighted_rating': weighted_rating
            })
        
        rated_products.sort(key=lambda x: x['weighted_rating'], reverse=True)
        product_ids_ordered = [p['product_id'] for p in rated_products[:limit]]
        
        if not product_ids_ordered:
            return []
        
        products_dict = {
            p.id: p for p in Producto.objects.filter(
                id__in=product_ids_ordered,
                activo=True,
                stock__gt=0
            ).select_related('categoria')
        }
        
        products = [products_dict[pid] for pid in product_ids_ordered if pid in products_dict]
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    def get_new_arrivals(self, limit=10):
        """New products"""
        from .models import Producto
        
        cache_key = f'new_arrivals_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        products = list(
            Producto.objects.filter(
                activo=True,
                stock__gt=0
            ).select_related('categoria').order_by('-fecha_creacion')[:limit]
        )
        
        cache.set(cache_key, products, self.cache_timeout)
        return products
    
    # ========== HOMEPAGE RECOMMENDATIONS ==========
    
    def get_homepage_recommendations(self):
        """Mix of recommendations for homepage"""
        recommendations = {
            'personalized': self.get_personalized_recommendations(limit=8),
            'trending': self.get_trending_products(limit=6),
            'popular': self.get_popular_products(limit=6),
            'new_arrivals': self.get_new_arrivals(limit=6),
        }
        
        from .models import ProductRating
        if ProductRating.objects.exists():
            recommendations['best_rated'] = self.get_best_rated_products(limit=6)
        
        return recommendations
    
    # ========== UTILITY METHODS ==========
    
    def clear_user_cache(self):
        """
        Limpiar caché de recomendaciones del usuario
        MEJORADO: Sin usar delete_pattern
        """
        if self.user:
            # Borrar claves específicas con límites comunes
            for limit in [6, 8, 10, 12, 15, 20]:
                cache.delete(f'personalized_recs_{self.user.id}_{limit}')
                cache.delete(f'collaborative_recs_{self.user.id}_{limit}')
    
    def calculate_recommendation_score(self, product):
        """
        Calcula un score de recomendación para un producto
        NUEVA FUNCIÓN: Score inteligente
        """
        from .models import ProductView, ProductRating
        
        score = 0.0
        
        # Factor 1: Popularidad (vistas últimos 30 días) - 30%
        recent_views = ProductView.objects.filter(
            product=product,
            viewed_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        score += min(recent_views / 100, 1.0) * 0.3
        
        # Factor 2: Rating promedio - 30%
        avg_rating = ProductRating.objects.filter(
            product=product
        ).aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            score += (avg_rating / 5.0) * 0.3
        
        # Factor 3: Novedad - 20%
        days_old = (timezone.now() - product.fecha_creacion).days
        freshness = max(0, 1 - (days_old / 365))
        score += freshness * 0.2
        
        # Factor 4: Disponibilidad - 20%
        if product.stock > 10:
            score += 0.2
        elif product.stock > 0:
            score += 0.1
        
        return score


# ========== HELPER FUNCTIONS ==========

def track_product_view(request, product):
    """
    Track when a user views a product
    MEJORADO: Mejor manejo de invalidación de caché
    """
    from .models import ProductView
    
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key if not user else None
    
    recent_threshold = timezone.now() - timedelta(minutes=5)
    
    recent_view = ProductView.objects.filter(
        product=product,
        viewed_at__gte=recent_threshold
    )
    
    if user:
        recent_view = recent_view.filter(user=user)
    else:
        recent_view = recent_view.filter(session_key=session_key)
    
    if recent_view.exists():
        return
    
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    ProductView.objects.create(
        user=user,
        product=product,
        session_key=session_key,
        ip_address=ip_address
    )
    
    # MEJORADO: No invalidar cache en cada vista
    # El cache expirará naturalmente según CACHE_TIMEOUT


def track_search_query(request, query, results_count):
    """Track user searches"""
    from .models import SearchQuery
    
    query = query.strip().lower()
    
    if len(query) < 2:
        return
    
    SearchQuery.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key if not request.user.is_authenticated else None,
        query=query,
        results_count=results_count
    )


def track_cart_addition(request, product, quantity=1):
    """Track when a product is added to cart"""
    from .models import CartInteraction
    
    CartInteraction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        product=product,
        session_key=request.session.session_key if not request.user.is_authenticated else None,
        quantity=quantity
    )
    
    # Invalidar caché de recomendaciones del usuario
    if request.user.is_authenticated:
        engine = RecommendationEngine(user=request.user)
        engine.clear_user_cache()


def get_recommendations_for_cart(cart_items, limit=6):
    """Recomendaciones basadas en productos en el carrito"""
    from .models import Purchase, Producto
    
    if not cart_items:
        return []
    
    product_ids = [item.product_id for item in cart_items]
    
    related_purchases = Purchase.objects.filter(
        product_id__in=product_ids
    ).values_list('user_id', flat=True).distinct()
    
    recommendations = Purchase.objects.filter(
        user_id__in=related_purchases
    ).exclude(
        product_id__in=product_ids
    ).values('product_id').annotate(
        count=Count('id')
    ).order_by('-count')[:limit].values_list('product_id', flat=True)
    
    return Producto.objects.filter(
        id__in=recommendations,
        activo=True,
        stock__gt=0
    ).select_related('categoria')