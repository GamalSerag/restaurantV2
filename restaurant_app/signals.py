from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import MenuItem
import firebase_admin
from firebase_admin import storage

@receiver(post_delete, sender=MenuItem)
def delete_image_from_firebase(sender, instance, **kwargs):
    if instance.image_url:
        # Assume image_url is the full URL to the Firebase storage location
        try:
            # Extract the file path from the full URL
            bucket = storage.bucket()
            # Example URL: "https://firebasestorage.googleapis.com/v0/b/projectname.appspot.com/o/images%2Fimage.jpg"
            # You need to extract the path "images/image.jpg" from the URL
            blob_name = instance.image_url.split('o/')[1].split('?')[0].replace('%2F', '/')
            blob = bucket.blob(blob_name)
            blob.delete()
            print("Firebase storage file deleted successfully")
        except Exception as e:
            print("Error deleting the Firebase storage file:", e)



# when update mMenuItem image_url delete the old image from firebase storage 
@receiver(pre_save, sender=MenuItem)
def delete_old_image_from_firebase(sender, instance, **kwargs):
    if not instance.pk:
        return  # If new instance, return because there's no previous image to delete

    try:
        # Get the old image URL from the database
        old_instance = MenuItem.objects.get(pk=instance.pk)
        old_image_url = old_instance.image_url
        new_image_url = instance.image_url

        if old_image_url and old_image_url != new_image_url:
            # Initialize the storage bucket
            bucket = storage.bucket()
            blob_name = old_image_url.split('o/')[1].split('?')[0].replace('%2F', '/')
            blob = bucket.blob(blob_name)
            blob.delete()
            print("Old Firebase storage file deleted successfully")
    except Exception as e:
        print("Error deleting the old Firebase storage file:", e) 