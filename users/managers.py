from django.apps import apps
from django.contrib.auth.hashers import make_password

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model, handling user creation and retrieval.

    Attributes:
        use_in_migrations (bool): Indicates whether this manager can be used in migrations.
    """
    use_in_migrations = True
    
    def _create_user_object(self, email, password, **extra_fields):
        """
        Create a user object without saving it to the database.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
            extra_fields (dict): Additional fields for the user.

        Returns:
            User: The user object with the password hashed.
        """
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        return user
    
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user to the database.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
            extra_fields (dict): Additional fields for the user.

        Returns:
            User: The saved user instance.
        """
        user = self._create_user_object(email, password, **extra_fields)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, first_name='', last_name='', phone='', **extra_fields):
        """
        Create a regular user with the given email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            phone (str): The phone number of the user.
            extra_fields (dict): Additional fields for the user.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The created user instance.
        """        
        if not email:
            raise ValueError('Users must have an email address.')

        user = self.model(
            email=self.normalize_email(email),
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.last_name = last_name
        user.first_name = first_name
        user.phone = phone
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create a superuser with the given email and password.

        Args:
            email (str): The email address of the superuser.
            password (str): The password of the superuser.
            extra_fields (dict): Additional fields for the superuser.

        Raises:
            ValueError: If is_staff or is_superuser is not set to True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Retrieve a user by their natural key (email).

        Args:
            username (str): The email address of the user.

        Returns:
            User: The user instance matching the email address.
        """
        return self.get(**{'%s__iexact' % self.model.USERNAME_FIELD: username})
