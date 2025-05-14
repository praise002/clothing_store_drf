from django.db import models
from django.utils import timezone

class GetOrNoneQuerySet(models.QuerySet):
    """Custom QuerySet that supports get_or_none()"""
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects"""
    def get_queryset(self):
        return GetOrNoneQuerySet(self.model, using=self._db)
    
    def get_or_none(self, **kwargs):
        return self.get_queryset().get_or_none(**kwargs)
    
class IsDeletedQuerySet(GetOrNoneQuerySet):
    def delete(self, hard_delete=False):
        if hard_delete:
            # Perform a hard delete
            return super().delete()
        else:
            # Perform a soft delete
            return self.update(is_deleted=True, deleted=timezone.now())
        
class IsDeletedManager(GetOrNoneManager):
    def get_queryset(self):
        return IsDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)
    
    def unfiltered(self):
        return IsDeletedQuerySet(self.model, using=self._db) # No filter applied here
    
    def hard_delete(self):
        return self.unfiltered().delete(hard_delete=True)