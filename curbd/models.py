from django.db import models
import datetime
import pytz


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=datetime.datetime.now(pytz.utc))

    def restore(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=None)

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()


class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.include_deleted = kwargs.pop('include_deleted', False)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not self.include_deleted:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(include_deleted=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = datetime.datetime.now(pytz.utc)
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()
